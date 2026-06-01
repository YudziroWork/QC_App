import fitz
import re
import os
from datetime import datetime
from create_report.core.readers.base_reader import BaseReader


class PdfReportReader(BaseReader):
    KEYWORD_NUMBER = ("номер:", "license plate number: ")
    KEYWORD_DATE = ("дата фиксации:", "recognition date:")
    KEYWORD_PERIOD = ("период:", "report period:")

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read(self) -> list:
        records = []

        try:
            pdf = fitz.open(self.file_path)

            # первая страница — ищем "Период"
            first_page_text = pdf[0].get_text()
            start_time = self._parse_period(first_page_text)
            print(f"DEBUG start_time='{start_time}'")

            numbers = []

            # каждая страница — ищем "Номер" и "Дата фиксации"
            for page in pdf:
                text = page.get_text()
                lines = text.split("\n")

                number = None
                date_str = None

                for i, line in enumerate(lines):
                    if any(kw in line.lower() for kw in self.KEYWORD_NUMBER):
                        for kw in self.KEYWORD_NUMBER:
                            if kw in line.lower():
                                after = line.lower().split(kw, 1)[1].strip()
                                if after:
                                    number = line.split(":", 1)[1].strip()
                                else:
                                    if i + 1 < len(lines):
                                        number = lines[i + 1].strip()
                                break

                    if any(kw in line.lower() for kw in self.KEYWORD_DATE):
                        for kw in self.KEYWORD_DATE:
                            if kw in line.lower():
                                after = line.lower().split(kw, 1)[1].strip()
                                if after:
                                    date_str = line.split(":", 1)[1].strip()
                                else:
                                    if i + 1 < len(lines):
                                        date_str = lines[i + 1].strip()
                                break

                if number:
                    adjusted_time = self._adjust_time(date_str, start_time)
                    numbers.append({
                        "number": number,
                        "time": adjusted_time,
                        "images": self._extract_images(page, number)
                    })


            pdf.close()

            records = numbers

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Ошибка обработки PDF: {type(e).__name__}: {e}")

        return records

    def _parse_period(self, text: str) -> datetime:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in self.KEYWORD_PERIOD):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    raw = parts[1].strip()
                    tokens = [t for t in raw.split(" ") if t]

                    # русский формат: от 21.04.2026 13:04:00 до ...
                    if len(tokens) >= 3 and tokens[0].lower() in ("от",):
                        start_str = tokens[1] + " " + tokens[2]
                        formats = [
                            "%d.%m.%Y %H:%M:%S",
                            "%d.%m.%Y %H:%M:%S.%f",
                            "%m/%d/%Y %I:%M:%S %p",
                            "%m/%d/%Y %I:%M:%S.%f %p",
                        ]
                        for fmt in formats:
                            try:
                                return datetime.strptime(start_str, fmt)
                            except ValueError:
                                continue

                # английский формат: from 5/25/2026 2:00:00 PM to ...
                full_line = line + (" " + lines[i + 1] if i + 1 < len(lines) else "")
                match = re.search(r'from\s+(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)', full_line,
                                  re.IGNORECASE)
                if match:
                    try:
                        return datetime.strptime(match.group(1), "%m/%d/%Y %I:%M:%S %p")
                    except ValueError:
                        pass

        return datetime(2000, 1, 1, 0, 0, 0)

    def _adjust_time(self, time_str: str, start_time: datetime) -> str:
        if not time_str:
            return "00:00:00"
        try:
            formats = [
                "%d.%m.%Y %H:%M:%S",
                "%d.%m.%Y %H:%M:%S.%f",
                "%m/%d/%Y %I:%M:%S %p",
                "%m/%d/%Y %I:%M:%S.%f %p",
            ]
            record_time = None
            for fmt in formats:
                try:
                    record_time = datetime.strptime(time_str.strip(), fmt)
                    break
                except ValueError:
                    continue

            if record_time is None:
                return "00:00:00"

            delta = record_time - start_time
            total_seconds = int(delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        except Exception:
            return "00:00:00"

    def _extract_images(self, page, number: str) -> list:
        import base64
        images = []
        text = page.get_text()
        print(f"DEBUG extract_images: number='{number}' in page text: {number in text}")
        print(f"DEBUG page images count: {len(page.get_images(full=True))}")
        if number not in text:
            return images
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            images.append(f"data:image/{ext};base64,{b64}")
        print(f"DEBUG extracted {len(images)} images")
        return images

