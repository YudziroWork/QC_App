import fitz
import re
import os
from datetime import datetime
from create_report.core.readers.base_reader import BaseReader


class PdfReportReader(BaseReader):
    KEYWORD_NUMBER = "номер:"
    KEYWORD_DATE = "дата фиксации:"
    KEYWORD_PERIOD = "период:"

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
                    if self.KEYWORD_NUMBER.lower() in line.lower():
                        # значение на следующей строке
                        if i + 1 < len(lines):
                            number = lines[i + 1].strip()

                    if self.KEYWORD_DATE.lower() in line.lower():
                        # значение на следующей строке
                        if i + 1 < len(lines):
                            date_str = lines[i + 1].strip()

                if number:
                    adjusted_time = self._adjust_time(date_str, start_time)
                    print(f"DEBUG number='{number}' date_str='{date_str}' time='{adjusted_time}'")
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
            if self.KEYWORD_PERIOD.lower() in line.lower():
                parts = line.split(":", 1)
                if len(parts) > 1:
                    raw = parts[1].strip()
                    # фильтруем пустые элементы от двойных пробелов
                    tokens = [t for t in raw.split(" ") if t]
                    # tokens: ["от", "21.04.2026", "13:04:00", "до", ...]
                    if len(tokens) >= 3:
                        start_str = tokens[1] + " " + tokens[2]
                        return datetime.strptime(start_str, "%d.%m.%Y %H:%M:%S")

        return datetime(2000, 1, 1, 0, 0, 0)  # заглушка если не найден

    def _adjust_time(self, time_str: str, start_time: datetime) -> str:
        if not time_str:
            return "00:00:00"
        try:
            record_time = datetime.strptime(time_str.strip(), "%d.%m.%Y %H:%M:%S")
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