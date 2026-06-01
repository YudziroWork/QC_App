import json


def build_etalon_matches(results: list) -> dict:
    etalon_matches = {}
    for idx, item in enumerate(results):
        best = item["best_match"]
        color = item["color"]
        if best and color != "red":
            if best not in etalon_matches:
                etalon_matches[best] = []
            etalon_matches[best].append({
                "idx": idx,
                "recognized": item["recognized"],
                "etalon": best
            })
    return etalon_matches


def build_comparison_section(results: list, etalon_matches: dict) -> str:
    rows_html = ""
    cards_html = ""

    for idx, item in enumerate(results):
        recognized = item["recognized"]
        best = item["best_match"] or ""
        dist = item["distance"]
        time = item["time"]
        color = item["color"]
        no_number = item.get("no_number", False)
        row_color = "gray" if no_number else color

        dist_display = "" if no_number else str(dist)
        dist_val = -1 if no_number else dist

        if best and best in etalon_matches and len(etalon_matches[best]) > 1:
            matches_json = json.dumps(etalon_matches[best], ensure_ascii=False)
            etalon_cell = (
                f'<span class="link" '
                f'onclick="openModal(this, {idx})">'
                f'{best}</span>'
            )
        else:
            etalon_cell = best

        rows_html += (
            f'<tr data-color="{row_color}" class="{row_color}">'
            f'<td><span class="link" onclick="openRecord({idx})">{recognized}</span></td>'
            f'<td>{etalon_cell}</td>'
            f'<td data-val="{dist_val}">{dist_display}</td>'
            f'<td>{time}</td>'
            f'</tr>\n'
        )

        cards_html += _build_record_card(idx, item)

    # Строим JS объект с данными для модалов эталонов
    etalon_modal_data = {}
    for etalon, matches in etalon_matches.items():
        if len(matches) > 1:
            etalon_modal_data[etalon] = matches

    etalon_data_js = f"<script>window.__etalonModalData = {json.dumps(etalon_modal_data, ensure_ascii=False)};</script>"

    table_html = f"""
{etalon_data_js}
<div id="comparison-filters" class="filters">
  <button class="filter-btn green"  onclick="toggleFilter('green',  this)">🟢 Полное совпадение</button>
  <button class="filter-btn yellow" onclick="toggleFilter('yellow', this)">🟡 Частичное</button>
  <button class="filter-btn red"    onclick="toggleFilter('red',    this)">🔴 Неверное</button>
  <button class="filter-btn gray"   onclick="toggleFilter('gray',   this)">⚫ Нет номера</button>
</div>
<div style="margin-bottom:1rem">
  <input id="search-input" type="text" placeholder="Поиск по номеру или эталону..."
    oninput="applySearch()"
    style="width:100%;padding:8px 14px;border-radius:10px;border:1px solid #ddd;
           font-size:14px;outline:none;background:#fff;">
</div>
<div id="comparison-table-wrap" class="table-wrap">
  <table id="comparison-table">
    <thead>
      <tr>
        <th onclick="sortTable(0)">Распознанный номер<span class="sort-icon">⇅</span></th>
        <th onclick="sortTable(1)">Эталон<span class="sort-icon">⇅</span></th>
        <th onclick="sortTable(2)">Расстояние<span class="sort-icon">⇅</span></th>
        <th onclick="sortTable(3)">Время<span class="sort-icon">⇅</span></th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>
"""
    return table_html + cards_html


def build_stats_section(stats: dict, etalon_matches: dict) -> str:
    duplicates = {k: v for k, v in etalon_matches.items() if len(v) >= 2}
    duplicates_data_js = f"<script>window.__duplicatesData = {json.dumps(duplicates, ensure_ascii=False)};</script>"

    missed_items = "".join(
        f'<div class="stat-row"><span>{n}</span></div>'
        for n in stats.get("missed", [])
    )
    missed_block = f"""
<div class="stat-block">
  <h4>Пропущенные номера</h4>
  {missed_items if missed_items else '<div class="stat-row"><span>Нет</span></div>'}
</div>""" if stats.get("missed") else ""

    return f"""
{duplicates_data_js}
<div class="stats-grid">
  <div class="stat-block">
    <h4>Статистика распознавания</h4>
    <div class="stat-row">
      <span>Всего распознано</span>
      <span class="stat-val">{stats["total"]}</span>
    </div>
    <div class="stat-row">
      <span><a class="link" onclick="switchToFilter('green')">Полностью распознано</a></span>
      <span class="stat-val">{stats["fully"]}</span>
    </div>
    <div class="stat-row">
      <span><a class="link" onclick="switchToFilter('yellow')">Частично распознано</a></span>
      <span class="stat-val">{stats["partial"]}</span>
    </div>
    <div class="stat-row">
      <span><a class="link" onclick="switchToFilter('red')">Неверно распознано</a></span>
      <span class="stat-val">{stats["incorrect"]}</span>
    </div>
    <div class="stat-row">
      <span><a class="link" onclick="switchToFilter('gray')">Без номера</a></span>
      <span class="stat-val">{stats["without_number"]}</span>
    </div>
    <div class="stat-row">
      <span><a class="link" onclick="openDuplicatesModal(window.__duplicatesData)">Число повторов</a></span>
      <span class="stat-val">{stats["duplicates"]}</span>
    </div>
  </div>
  <div class="stat-block">
    <h4>Статистика детекции</h4>
    {_stat_rows([
        ("Всего записей в эталоне", stats["etalon_total"]),
        ("Обнаружено номеров эталона", stats["etalon_found"]),
        ("Пропущено номеров", stats["missed_count"]),
    ])}
  </div>
  <div class="stat-block">
    <h4>Качество (%)</h4>
    {_stat_rows([
        ("Полностью распознано", _pct(stats["fully"], stats["total"])),
        ("Частично распознано", _pct(stats["partial"], stats["total"])),
        ("Неверно распознано", _pct(stats["incorrect"], stats["total"])),
        ("Пропущено", _pct(stats["missed_count"], stats["etalon_total"])),
        ("Повторы", _pct(stats["duplicates"], stats["total"])),
    ])}
  </div>
  <div class="stat-block">
    <h4>Strict</h4>
    {_stat_rows([
        ("Точность (%)", stats["precision_strict"]),
        ("Полнота (%)", stats["recall_strict"]),
        ("Конечная оценка (%)", stats["f1_strict"]),
    ])}
  </div>
  <div class="stat-block">
    <h4>Soft</h4>
    {_stat_rows([
        ("Точность (%)", stats["precision_soft"]),
        ("Полнота (%)", stats["recall_soft"]),
        ("Конечная оценка (%)", stats["f1_soft"]),
    ])}
  </div>
  {missed_block}
</div>
"""


def _build_record_card(idx: int, item: dict) -> str:
    recognized = item["recognized"]
    best = item["best_match"] or "—"
    dist = item["distance"]
    color = item["color"]
    no_number = item.get("no_number", False)
    images = item.get("images", [])

    if no_number:
        badge = '<span class="badge gray">Нет номера</span>'
        errors_html = ""
        dist_html = ""
    else:
        badge = f'<span class="badge {color}">' + {
            "green": "Полное совпадение",
            "yellow": "Частичное совпадение",
            "red": "Неверное распознавание"
        }.get(color, "") + '</span>'

        dist_html = f'<div class="label">Расстояние</div><div class="value">{dist}</div>'
        errors_html = _build_error_list(recognized, best, dist, color)

    images_html = "".join(
        f'<img class="plate" src="{src}" alt="Фото номера">'
        for src in images
    )

    return f"""<div id="record-{idx}" class="record-card" style="display:none">
  <button class="back-btn" onclick="backToTable()">← Назад</button>
  <div class="card">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem">
      <h3>{recognized}</h3>{badge}
    </div>
    <div class="label">Наилучшее совпадение с эталоном</div>
    <div class="value">{best}</div>
    {dist_html}
    {errors_html}
    {images_html}
  </div>
</div>"""


def _build_error_list(recognized: str, best: str, dist: int, color: str) -> str:
    if color == "gray" or not best or best == "—":
        return ""

    errors = []
    min_len = min(len(recognized), len(best))

    for i in range(min_len):
        if recognized[i] != best[i]:
            errors.append(f"{recognized[i]} → {best[i]}")

    if len(recognized) != len(best):
        errors.append(f"Длина отличается ({len(recognized)} → {len(best)})")

    if not errors:
        return ""

    items = "".join(f"<li>{e}</li>" for e in errors)
    return f"""
<div class="label" style="margin-top:.75rem">Ошибки</div>
<ul class="error-list">{items}</ul>
"""


def build_adv_stats_section(adv_stats: dict) -> str:
    etalon_rows = "".join(
        f'<tr><td><span class="link" onclick="searchEtalon(this.textContent.trim())">{etalon}</span></td><td>{count}</td></tr>'
        for etalon, count in sorted(
            adv_stats["etalon_usage"].items(), key=lambda x: -x[1]
        )
        if count >= 2
    )

    error_rows = "".join(
        f"<tr><td>{error}</td><td>{count}</td></tr>"
        for error, count in sorted(
            adv_stats["error_stats"].items(), key=lambda x: -x[1]
        )
    )

    return f"""
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:1rem">
  <div class="table-wrap">
    <table>
      <thead><tr><th>Эталон</th><th>Количество совпадений</th></tr></thead>
      <tbody>{etalon_rows}</tbody>
    </table>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Ошибка</th><th>Количество</th></tr></thead>
      <tbody>{error_rows}</tbody>
    </table>
  </div>
</div>
"""


def _stat_rows(pairs: list) -> str:
    return "".join(
        f'<div class="stat-row"><span>{label}</span>'
        f'<span class="stat-val">{value}</span></div>'
        for label, value in pairs
    )


def _pct(a: int, b: int) -> str:
    return f"{round(a / b * 100, 2)}" if b else "0"