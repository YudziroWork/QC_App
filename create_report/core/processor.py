from create_report.core.report.regression_report import RegressionReport
from create_report.core.readers.xlsx_reader import EtalonReader, ReportReader
from create_report.core.readers.pdf_reader import PdfReportReader
from create_report.core.comparison.comparator import compare
from create_report.core.stats.stats import calculate_statistics
from create_report.core.report.html_report import HtmlReport


def run(etalon_path: str, report_path: str, output_path: str, report_format: str = "xlsx", show_settings: bool = False):
    try:
        etalon = EtalonReader(etalon_path).read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл эталона не найден: {etalon_path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла эталона: {e}")

    try:
        if report_format == "xlsx":
            keywords = ReportReader(report_path).read_keywords()
        else:
            keywords = []
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении ключевых слов отчёта: {e}")

    try:
        if report_format == "xlsx":
            report = ReportReader(report_path).read()
        elif report_format == "pdf":
            report = PdfReportReader(report_path).read()
        else:
            raise NotImplementedError()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл отчёта не найден: {report_path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла отчёта: {e}")

    try:
        results = compare(etalon, report)
        stats = calculate_statistics(results, etalon)
    except Exception as e:
        raise RuntimeError(f"Ошибка при сравнении данных: {e}")

    try:
        HtmlReport().generate(
            results=results,
            stats=stats,
            output_path=output_path,
            keywords=keywords,
            etalon_path=etalon_path,
            report_path=report_path,
        )
    except PermissionError:
        raise PermissionError(f"Файл отчёта открыт в другой программе: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании отчёта: {e}")


def run_regression(groups: list, output_path: str, country: str, version: str):
    datasets = []

    for group in groups:
        name = group["name"]
        etalon_path = group["etalon_path"]
        report_path = group["report_path"]

        try:
            etalon = EtalonReader(etalon_path).read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл эталона не найден: {etalon_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении эталона группы '{name}': {e}")

        try:
            keywords = ReportReader(report_path).read_keywords()
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении ключевых слов группы '{name}': {e}")

        try:
            report = ReportReader(report_path).read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл отчёта не найден: {report_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении отчёта группы '{name}': {e}")

        try:
            results = compare(etalon, report)
            stats = calculate_statistics(results, etalon)
        except Exception as e:
            raise RuntimeError(f"Ошибка при сравнении данных группы '{name}': {e}")

        datasets.append({
            "name": name,
            "stats": stats,
            "keywords": keywords
        })

    try:
        RegressionReport().generate(datasets, output_path, country, version)
    except PermissionError:
        raise PermissionError(f"Файл отчёта открыт в другой программе: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании регрессионного отчёта: {e}")