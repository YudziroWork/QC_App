import os
from create_report.core.report.regression_html_templates import get_regression_base_template
from create_report.core.report.regression_html_sections import (
    build_regression_header,
    build_versions_and_settings,
    build_results_table,
)


class RegressionHtmlReport:

    def generate(
        self,
        datasets: list,
        output_path: str,
        country: str,
        version: str,
        groups: list,
    ):
        title = f"Регресс версии {version}"

        header = build_regression_header(version, country, groups)
        versions_settings = build_versions_and_settings(datasets, country)
        results = build_results_table(datasets, country)

        body = header + versions_settings + results

        html = get_regression_base_template(title=title, body=body)

        if not output_path.endswith(".html"):
            output_path += ".html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)