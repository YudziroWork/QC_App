import os
from create_report.core.settings_reader import get_settings
from version_detector import find_version


def build_regression_header(version: str, country: str, groups: list) -> str:
    # Блоки файлов по группам
    group_cards = ""
    for group in groups:
        etalon_name = os.path.basename(group["etalon_path"])
        report_name = os.path.basename(group["report_path"])
        group_cards += f"""
<div class="group-card">
  <h4>{group["name"]}</h4>
  <div class="group-file"><span>Эталон:</span> {etalon_name}</div>
  <div class="group-file"><span>Отчёт:</span> {report_name}</div>
</div>"""

    return f"""
<div class="report-header">
  <div class="report-title">Регресс версии {version}</div>
  <div class="report-meta">Страна: {country}</div>
</div>
<div class="section">
  <div class="section-title">Файлы</div>
  <div class="groups-row">
    {group_cards}
  </div>
</div>
"""


def build_versions_and_settings(datasets: list, country: str) -> str:
    # Версии ПО — единые для всех групп
    versions = [
        ("Securos", find_version("SecurOS")),
        ("Auto", find_version("SecurOS Auto")),
        ("NN-server Auto", find_version("SecurOS NN-Server Auto for Intel")),
        ("NN-server Vehicle", find_version("SecurOS NN-Server Vehicle for Intel")),
    ]

    versions_rows = "".join(
        f"<tr><td>{name}</td><td>{ver}</td></tr>"
        for name, ver in versions
    )

    versions_block = f"""
<div class="table-block" style="min-width:220px">
  <h4>Версии ПО</h4>
  <table>
    <thead><tr><th>Компонент</th><th>Версия</th></tr></thead>
    <tbody>{versions_rows}</tbody>
  </table>
</div>"""

    # Таблицы настроек — по одной на каждый keyword каждой группы
    settings_blocks = ""
    for dataset in datasets:
        name = dataset["name"]
        keywords = dataset["keywords"]

        for keyword in keywords:
            settings = get_settings([keyword])
            title = f"{name} | {keyword}"

            if settings:
                s = settings[0]["params"]

                mode = s.get("mode", "")
                if mode == "0":
                    mode_val = "Высокая скорость"
                elif mode == "2":
                    mode_val = "Низкая скорость"
                elif mode == "3":
                    mode_val = "Stop & Go"
                else:
                    mode_val = mode

                tracking = s.get("tracking_mode", "")
                if tracking == "0":
                    tracking_val = "Дорога/шоссе"
                elif tracking == "1":
                    tracking_val = "Парковка"
                elif tracking == "2":
                    tracking_val = "Мобильный"
                else:
                    tracking_val = tracking

                rows = f"""
<tr><td>Символ короче</td><td>{s.get("min_height_symbol", "—")}</td></tr>
<tr><td>Символ длиннее</td><td>{s.get("max_height_symbol", "—")}</td></tr>
<tr><td>Номер уже был распознан</td><td>{s.get("same_number_time", "—")}</td></tr>
<tr><td>Качество распознавания</td><td>{s.get("quality", "—")}</td></tr>
<tr><td>Тип распознавателя</td><td>{mode_val}</td></tr>
<tr><td>Режим работы распознавателя</td><td>{tracking_val}</td></tr>"""
            else:
                rows = "<tr><td colspan='2'>Настройки не найдены</td></tr>"

            settings_blocks += f"""
<div class="table-block" style="min-width:260px">
  <h4>{title}</h4>
  <table>
    <thead><tr><th>Настройка</th><th>Значение</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""

    return f"""
<div class="section">
  <div class="section-title">Версии ПО и настройки</div>
  <div class="versions-settings-row">
    {versions_block}
    {settings_blocks}
  </div>
</div>
"""


def build_results_table(datasets: list, country: str) -> str:
    rows = ""
    for dataset in datasets:
        name = dataset["name"]
        stats = dataset["stats"]
        region = f"{country} — {name}"

        fully_pct = round(stats["f1_strict"], 2)
        soft_pct = round(stats["f1_soft"], 2)
        missed_pct = round(
            stats["missed_count"] / stats["etalon_total"] * 100, 2
        ) if stats["etalon_total"] else 0
        dup_pct = round(
            stats["duplicates"] / stats["total"] * 100, 2
        ) if stats["total"] else 0

        rows += f"""
<tr>
  <td>{region}</td>
  <td>{fully_pct}</td>
  <td>{soft_pct}</td>
  <td>{missed_pct}</td>
  <td>{dup_pct}</td>
  <td class="wip-cell">—</td>
  <td class="wip-cell">—</td>
</tr>"""

    return f"""
<div class="section">
  <div class="section-title">Результаты</div>
  <div class="results-table-wrap">
    <table>
      <thead>
        <tr>
          <th>Тип распознователя</th>
          <th>Полное совпадение (%)</th>
          <th>Включая ошибочные (%)</th>
          <th>Пропущено (%)</th>
          <th>Повторов (%)</th>
          <th>Изменения распознавания (%)</th>
          <th>Изменения детекции (%)</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</div>
"""