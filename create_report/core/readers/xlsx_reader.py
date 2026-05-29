from datetime import datetime
from openpyxl import load_workbook
from create_report.core.readers.base_reader import BaseReader
import pandas as pd

class EtalonReader(BaseReader):
    def read(self)->list:
        wb=load_workbook(self.file_path)
        ws=wb.active

        number=[]
        for row in ws.iter_rows(min_col=1, max_col=1, values_only=True):
            value = row[0]
            if value is not None:
                number.append(str(value).strip().upper())
        return number




class ReportReader(BaseReader):
    def read(self) -> list:
        df = pd.read_excel(self.file_path, header=None, engine='calamine')

        start_time = self._parse_period(df.iloc[2, 0])  # A3 → строка 2, столбец 0
        records = []

        for _, row in df.iloc[11:].iterrows():  # с 12-й строки
            number = row.iloc[0]
            time_str = row.iloc[1]

            if pd.isna(number):
                break

            adjusted_time = self._adjust_time(str(time_str), start_time)
            records.append({
                "number": str(number).strip(),
                "time": adjusted_time
            })
        return records

    def read_keywords(self) -> list:
        df = pd.read_excel(self.file_path,engine='calamine')
        keywords = set()
        for value in df.iloc[11:, 2]:  # столбец C (индекс 2), с 12-й строки
            if pd.notna(value):
                keywords.add(str(value).strip())
        return list(keywords)

    def _parse_period(self, cell_value:str):
        parts= cell_value.split(" ")
        start_str=parts[2]+" "+parts[3]
        start_time=datetime.strptime(start_str,"%d.%m.%Y %H:%M:%S")
        return start_time

    def _adjust_time(self,time_str:str, start_time: datetime):
        if time_str is None:
            return "00:00:00"
        record_time = datetime.strptime(str(time_str).strip(), "%Y-%m-%d %H:%M:%S.%f")
        delta = record_time - start_time

        # timedelta в формат ЧЧ:ММ:СС
        total_seconds = int(delta.total_seconds())
        hours = total_seconds//3600
        minutes = (total_seconds%3600)//60
        seconds = total_seconds % 60

        return f"{hours:02}:{minutes:02}:{seconds:02}"