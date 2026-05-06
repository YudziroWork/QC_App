from create_report.core.readers.xlsx_reader import EtalonReader, ReportReader
from create_report.core.comparison.comparator import compare
from create_report.core.report.standart_report import StandardReport
from create_report.core.stats.stats import calculate_statistics

def run(etalon_path: str, report_path:str ,output_path:str, report_format: str = "xlsx"):
    try:
        etalon = EtalonReader(etalon_path).read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл эталона не найден{etalon_path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла эталона: {e}")

    try:
        if report_format=="xlsx":
            report = ReportReader(report_path).read()
        else:
            raise NotImplementedError()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл отчёта не найден: {report_path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла отчёта: {e}")

    try:
        results= compare(etalon,report)
        stats=calculate_statistics(results, etalon)
    except Exception as e:
        raise RuntimeError(f"Ошибка при сравнении данных: {e}")

    try:
        StandardReport().generate(results,stats, output_path)
    except PermissionError:
        raise PermissionError(f"Файл отчёта открыт в другой программе: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании отчёта: {e}")