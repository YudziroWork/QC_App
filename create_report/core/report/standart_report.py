from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from create_report.core.report.base_report import BaseReport
from create_report.config.settings import COLORS

class StandardReport(BaseReport):

    def _auto_width(self, ws):
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter  # буква столбца (A, B, C...)
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_length + 4  # +4 для отступа

    def generate(self,results: list, stats: dict, output_path:str):
        wb=Workbook()
        ws= wb.active
        ws.title="Отчёт"

        self._write_comparicon_table(ws, results)
        self._write_missed(ws, stats['missed'])
        self._write_stats(ws, stats)
        self._auto_width(ws)

        wb.save(output_path)

    # ─────────────────────────────────────────
    # Таблица сравнения A:D
    # ─────────────────────────────────────────

    def _write_comparicon_table(self, ws, results):
        headers = ["Распознанные", "Эталон", "Расстояние", "Время"]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col,value=header)
            self._style_header(cell)

        for row_idx, record in enumerate(results, start=2):
            values = [
                record["recognized"],
                record["best_match"] if record["best_match"] else "",
                record["distance"] if record["distance"] is not None else"",
                record["time"]
            ]
            fill = self._get_fill(record["color"])

            for col_idx, value in enumerate(values, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.fill = fill
                self._style_cell(cell)

    # ─────────────────────────────────────────
    # Пропущенные номера F:F
    # ─────────────────────────────────────────

    def _write_missed(self, ws, missed: list):
        header = ws.cell(row=1, column=6, value="Пропущенные номера")
        self._style_header(header)

        for row_idx, number in enumerate(missed, start=1):
            cell=ws.cell(row=row_idx+1, column=6, value=number)
            self._style_cell(cell)

    # ─────────────────────────────────────────
    # Статистика H:I и K:L
    # ─────────────────────────────────────────

    def _write_stats(self, ws, stats: dict):
        recognition_data = [
            ("Статистика распознания", None),
            ("Всего распознано", stats["total"]),
            ("Полностью распознано", stats["fully"]),
            ("Частично распознано", stats["partial"]),
            ("Неверно распознано", stats["incorrect"]),
            ("Без номера", stats["without_number"]),
            ("Число повторов", stats["duplicates"]),
        ]

        detection_data = [
            ("Статистика детекции", None),
            ("Всего записей в эталоне", stats["etalon_total"]),
            ("Обнаружено номеров эталона", stats["etalon_found"]),
            ("Пропущенные номера", stats["missed_count"]),
        ]

        quality_data = [
            ("Качество", None),
            ("Полностью распознано (%)", self._pct(stats["fully"], stats["total"])),
            ("Частично распознано (%)", self._pct(stats["partial"], stats["total"])),
            ("Неверно распознано (%)", self._pct(stats["incorrect"], stats["total"])),
            ("Пропущено (%)", self._pct(stats["missed_count"], stats["etalon_total"])),
            ("Повторы (%)", self._pct(stats["duplicates"], stats["total"])),
            ("Strict", None),
            ("Точность (%)", stats["precision_strict"]),
            ("Полнота (%)", stats["recall_strict"]),
            ("Конечная оценка (%)", stats["f1_strict"]),
            ("Soft", None),
            ("Точность (%)", stats["precision_soft"]),
            ("Полнота (%)", stats["recall_soft"]),
            ("Конечная оценка (%)", stats["f1_soft"]),
        ]

        self._write_block(ws, recognition_data, start_row=1, col_label=8, col_value=9)
        detection_start = 1 + len(recognition_data) + 2
        self._write_block(ws, detection_data, start_row=detection_start, col_label=8, col_value=9)
        self._write_block(ws, quality_data, start_row=1, col_label=11, col_value=12)

    def _write_block(self,ws,data: list, start_row: int, col_label: int,col_value: int):
        for i, (label, value) in enumerate(data):
            row=start_row + i
            label_cell = ws.cell(row=row, column=col_label, value=label)
            self._style_cell(label_cell)

            if value is not None:
                value_cell =ws.cell(row=row, column=col_value, value=value)
                self._style_cell(value_cell)

    # ─────────────────────────────────────────
    # Стили
    # ─────────────────────────────────────────
    def _style_header(self, cell):
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
        self._apply_border(cell)

    def _style_cell(self, cell):
        cell.alignment= Alignment(horizontal="center")
        self._apply_border(cell)

    def _apply_border(self, cell):
        thin=Side(style="thin")
        cell.border=Border(left=thin, right=thin, top=thin, bottom=thin)

    def _get_fill(self,color: str)->PatternFill:
        hex_color=COLORS.get(color, "FFFFFF")
        return PatternFill(start_color=hex_color, end_color=hex_color, fill_type='solid')

    def _pct(selfself, value: int,total: int)->float:
        if total == 0:
            return 0.0
        return round(value / total * 100, 2)

