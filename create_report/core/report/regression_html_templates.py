def get_regression_base_template(title: str, body: str) -> str:
    css = get_regression_css()
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"ru\">\n"
        "<head>\n"
        "<meta charset=\"UTF-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"<title>{title}</title>\n"
        "<style>\n" + css + "\n</style>\n"
        "</head>\n"
        "<body>\n"
        "<div class=\"container\">\n"
        + body +
        "\n</div>\n"
        "</body>\n"
        "</html>"
    )


def get_regression_css() -> str:
    return """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #f5f6fa; color: #1a1a1a; font-size: 14px; }
  .container { max-width: 1400px; margin: 0 auto; padding: 2rem 1rem; }

  /* Шапка */
  .report-title { font-size: 24px; font-weight: 700; margin-bottom: 6px; }
  .report-meta { font-size: 14px; color: #555; margin-bottom: 4px; }
  .report-header { margin-bottom: 1.5rem; padding-bottom: 1rem;
                   border-bottom: 2px solid #e5e5e5; }

  /* Файлы групп */
  .groups-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
  .group-card { background: #fff; border: 1px solid #e5e5e5; border-radius: 10px;
                padding: 1rem 1.25rem; flex: 1; min-width: 220px; }
  .group-card h4 { font-size: 13px; font-weight: 600; color: #185FA5;
                   margin-bottom: .5rem; text-transform: uppercase; letter-spacing: .5px; }
  .group-file { font-size: 13px; color: #555; margin-bottom: 3px; }
  .group-file span { color: #888; font-size: 12px; }

  /* Секция версий и настроек */
  .versions-settings-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }

  /* Таблицы */
  .table-block { background: #fff; border: 1px solid #e5e5e5;
                 border-radius: 10px; overflow: hidden; }
  .table-block h4 { font-size: 13px; font-weight: 600; color: #555;
                    padding: .75rem 1rem; background: #fafafa;
                    border-bottom: 1px solid #eee; }
  table { width: 100%; border-collapse: collapse; }
  th { padding: 8px 12px; background: #fafafa; color: #888;
       font-weight: 500; text-align: left; border-bottom: 2px solid #eee;
       font-size: 13px; }
  td { padding: 8px 12px; border-bottom: 1px solid #f5f5f5; font-size: 13px; }
  tr:last-child td { border-bottom: none; }

  /* Таблица результатов */
  .results-section { margin-bottom: 1.5rem; }
  .results-section h3 { font-size: 16px; font-weight: 600;
                        margin-bottom: .75rem; color: #333; }
  .results-table-wrap { background: #fff; border: 1px solid #e5e5e5;
                        border-radius: 10px; overflow: hidden; }
  .results-table-wrap table th { background: #f0f4fa; color: #555; }
  .wip-cell { color: #bbb; font-style: italic; font-size: 12px; }

  /* Секция */
  .section { margin-bottom: 2rem; }
  .section-title { font-size: 16px; font-weight: 600; color: #333;
                   margin-bottom: .75rem; padding-bottom: .4rem;
                   border-bottom: 1px solid #e5e5e5; }
"""