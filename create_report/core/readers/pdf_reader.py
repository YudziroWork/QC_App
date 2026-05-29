import fitz
import re
import os
from datetime import datetime
from create_report.core.readers.base_reader import BaseReader


class PdfReportReader(BaseReader):
    KEYWORD_NUMBER = ("номер:", "license plate number: ")
    KEYWORD_DATE = ("дата фиксации:", "recognition date:")
    KEYWORD_PERIOD = ("период:", "report period:")

    def __init__(self, file_path: str, output_path: str):
        super().__init__(file_path)
        self.output_path = output_path

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
                    #print(f"DEBUG number='{number}' date_str='{date_str}' time='{adjusted_time}'")
                    numbers.append({
                        "number": number,
                        "time": adjusted_time
                    })

            self._save_images(pdf, [r["number"] for r in numbers])
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
                        try:
                            return datetime.strptime(start_str, "%d.%m.%Y %H:%M:%S")
                        except ValueError:
                            pass

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
            formats = ["%d.%m.%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p"]
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

    def _save_images(self, pdf, numbers: list):
        img_folder = self._get_img_folder()
        os.makedirs(img_folder, exist_ok=True)

        for number in numbers:
            counter = 1
            safe_name = self._safe_filename(number)

            for page in pdf:
                if number not in page.get_text():
                    continue

                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    base_image = pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]

                    filename = f"{safe_name}.{ext}"
                    if os.path.exists(os.path.join(img_folder, filename)):
                        filename = f"{safe_name}_{counter}.{ext}"
                        counter += 1

                    filepath = os.path.join(img_folder, filename)
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)

    def _get_img_folder(self) -> str:
        return os.path.join(os.path.dirname(self.output_path), "img")

    def _safe_filename(self, number: str) -> str:
        if number.strip().lower() == "нет номера":
            return "Нет номера"
        return re.sub(r'[<>:"/\\|?*]', "", number)