import os
from create_report.core.report.html_templates import get_base_template
from create_report.core.report.html_sections import (
    build_comparison_section,
    build_stats_section,
    build_adv_stats_section,
    build_etalon_matches,
)
from create_report.core.stats.adv_stats import calculate_advanced_statistics


class HtmlReport:

    def generate(
        self,
        results: list,
        stats: dict,
        output_path: str,
        keywords: list = None,
        etalon_path: str = "",
        report_path: str = "",
    ):
        title = os.path.splitext(os.path.basename(output_path))[0]
        recognizer = ", ".join(keywords) if keywords else "—"
        etalon_name = os.path.basename(etalon_path) if etalon_path else "—"
        report_name = os.path.basename(report_path) if report_path else "—"

        etalon_matches = build_etalon_matches(results)

        comparison_html = build_comparison_section(results, etalon_matches)
        stats_html = build_stats_section(stats, etalon_matches)
        adv_stats = calculate_advanced_statistics(results)
        adv_stats_html = build_adv_stats_section(adv_stats)

        html = get_base_template(
            title=title,
            recognizer=recognizer,
            etalon_name=etalon_name,
            report_name=report_name,
            body=""
        )

        html = html.replace("%%COMPARISON%%", comparison_html)
        html = html.replace("%%STATS%%", stats_html)
        html = html.replace("%%ADV_STATS%%", adv_stats_html)

        if not output_path.endswith(".html"):
            output_path += ".html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)