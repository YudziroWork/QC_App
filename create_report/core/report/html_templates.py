def get_base_template(title: str, recognizer: str, etalon_name: str, report_name: str, body: str) -> str:
    css = get_css()
    js = get_js()
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
        "  <div class=\"header\">\n"
        f"    <h1 class=\"title\">{title}</h1>\n"
        "    <div class=\"meta\">\n"
        f"      <span class=\"meta-item\">{recognizer}</span>\n"
        "      <span class=\"meta-sep\">·</span>\n"
        f"      <span class=\"meta-item\">Эталон: {etalon_name}</span>\n"
        "      <span class=\"meta-sep\">·</span>\n"
        f"      <span class=\"meta-item\">Отчёт: {report_name}</span>\n"
        "    </div>\n"
        "  </div>\n"
        "  <nav class=\"tabs\">\n"
        "    <a class=\"tab active\" onclick=\"showTab('comparison')\">Таблица сравнения</a>\n"
        "    <a class=\"tab\" onclick=\"showTab('stats')\">Статистика</a>\n"
        "    <a class=\"tab\" onclick=\"showTab('adv-stats')\">Расширенная статистика</a>\n"
        "  </nav>\n"
        "  <div id=\"comparison\" class=\"tab-content active\">%%COMPARISON%%</div>\n"
        "  <div id=\"stats\" class=\"tab-content\">%%STATS%%</div>\n"
        "  <div id=\"adv-stats\" class=\"tab-content\">%%ADV_STATS%%</div>\n"
        "</div>\n"
        "<div id=\"modal\" class=\"modal-overlay\" onclick=\"closeModal()\">\n"
        "  <div class=\"modal-box\" onclick=\"event.stopPropagation()\">\n"
        "    <button class=\"modal-close\" onclick=\"closeModal()\">✕</button>\n"
        "    <div id=\"modal-content\"></div>\n"
        "  </div>\n"
        "</div>\n"
        "<script>\n" + js + "\n</script>\n"
        "</body>\n"
        "</html>"
    )


def get_css() -> str:
    return """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #f5f6fa; color: #1a1a1a; font-size: 14px; }
  .container { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }

  /* Шапка */
  .header { margin-bottom: 1.5rem; }
  .title { font-size: 22px; font-weight: 600; margin-bottom: 6px; }
  .meta { display: flex; gap: 8px; flex-wrap: wrap; color: #666; font-size: 13px; }
  .meta-sep { color: #ccc; }

  /* Вкладки */
  .tabs { display: flex; gap: 4px; margin-bottom: 1.5rem;
          border-bottom: 2px solid #e5e5e5; }
  .tab { padding: 8px 18px; cursor: pointer; border-radius: 8px 8px 0 0;
         color: #666; text-decoration: none; user-select: none;
         border: 1px solid transparent; border-bottom: none;
         transition: background .15s; }
  .tab:hover { background: #eee; }
  .tab.active { background: #fff; color: #185FA5; border-color: #e5e5e5;
                margin-bottom: -2px; font-weight: 500; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Фильтры */
  .filters { display: flex; gap: 8px; margin-bottom: 1rem; flex-wrap: wrap; }
  .filter-btn { padding: 5px 14px; border-radius: 20px; border: 2px solid transparent;
                cursor: pointer; font-size: 13px; background: #f0f0f0; color: #555;
                transition: all .15s; }
  .filter-btn:hover { opacity: .85; }
  .filter-btn.active { font-weight: 600; }
  .filter-btn.green  { border-color: #4CAF50; }
  .filter-btn.green.active  { background: #eaf3de; color: #2e6b0e; }
  .filter-btn.yellow { border-color: #FFC107; }
  .filter-btn.yellow.active { background: #fff8e1; color: #856404; }
  .filter-btn.red    { border-color: #F44336; }
  .filter-btn.red.active    { background: #fdecea; color: #b71c1c; }
  .filter-btn.gray   { border-color: #9E9E9E; }
  .filter-btn.gray.active   { background: #f5f5f5; color: #424242; }

  /* Таблица */
  .table-wrap { background: #fff; border-radius: 12px;
                border: 1px solid #e5e5e5; overflow: hidden; }
  table { width: 100%; border-collapse: collapse; }
  th { padding: 10px 14px; background: #fafafa; color: #888;
       font-weight: 500; text-align: left; border-bottom: 2px solid #eee;
       white-space: nowrap; user-select: none; cursor: pointer; }
  th:hover { background: #f0f0f0; }
  th .sort-icon { margin-left: 4px; opacity: .4; font-size: 11px; }
  td { padding: 9px 14px; border-bottom: 1px solid #f5f5f5; }
  tr:last-child td { border-bottom: none; }
  tr.green  td:first-child { border-left: 3px solid #4CAF50; }
  tr.yellow td:first-child { border-left: 3px solid #FFC107; }
  tr.red    td:first-child { border-left: 3px solid #F44336; }
  tr.gray   td:first-child { border-left: 3px solid #9E9E9E; }
  tr[data-color="green"]  { background: #f9fff7; }
  tr[data-color="yellow"] { background: #fffef5; }
  tr[data-color="red"]    { background: #fff9f9; }
  tr[data-color="gray"]   { background: #fafafa; }

  /* Ссылки в таблице */
  .link { cursor: pointer; color: #185FA5; text-decoration: underline dotted; }
  .link:hover { text-decoration: underline; }

  /* Карточка номера */
  .card { background: #fff; border-radius: 12px; border: 1px solid #e5e5e5;
          padding: 1.5rem; margin-bottom: 1rem; }
  .card h3 { font-size: 18px; margin-bottom: .75rem; }
  .card .label { font-size: 12px; color: #888; margin-bottom: 2px; }
  .card .value { font-size: 15px; margin-bottom: 1rem; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 12px;
           font-size: 12px; font-weight: 600; }
  .badge.green  { background: #eaf3de; color: #2e6b0e; }
  .badge.yellow { background: #fff8e1; color: #856404; }
  .badge.red    { background: #fdecea; color: #b71c1c; }
  .badge.gray   { background: #f5f5f5; color: #424242; }
  .error-list { list-style: none; padding: 0; }
  .error-list li { font-size: 13px; color: #555; padding: 3px 0;
                   border-bottom: 1px solid #f0f0f0; }
  .back-btn { background: none; border: 1px solid #ccc; border-radius: 8px;
              padding: 6px 14px; font-size: 13px; cursor: pointer;
              color: #666; margin-bottom: 1rem; }
  .back-btn:hover { background: #f5f5f5; }
  img.plate { max-width: 100%; border-radius: 8px; margin-top: 8px; border: 1px solid #eee; }

  /* Статистика */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 1rem; }
  .stat-block { background: #fff; border-radius: 12px; border: 1px solid #e5e5e5;
                padding: 1.25rem; }
  .stat-block h4 { font-size: 14px; color: #888; margin-bottom: .75rem;
                   text-transform: uppercase; letter-spacing: .5px; }
  .stat-row { display: flex; justify-content: space-between; padding: 5px 0;
              border-bottom: 1px solid #f5f5f5; font-size: 14px; }
  .stat-row:last-child { border-bottom: none; }
  .stat-val { font-weight: 500; }

  /* Модал */
  .modal-overlay { display: none; position: fixed; inset: 0;
                   background: rgba(0,0,0,.4); z-index: 1000;
                   align-items: center; justify-content: center; }
  .modal-overlay.open { display: flex; }
  .modal-box { background: #fff; border-radius: 14px; padding: 1.5rem;
               min-width: 320px; max-width: 560px; width: 90%;
               max-height: 80vh; overflow-y: auto; position: relative; }
  .modal-close { position: absolute; top: 12px; right: 14px; background: none;
                 border: none; font-size: 18px; cursor: pointer; color: #888; }
  .modal-title { font-size: 16px; font-weight: 600; margin-bottom: 1rem; }
  .modal-item { padding: 7px 0; border-bottom: 1px solid #f0f0f0;
                font-size: 14px; }
  .modal-item:last-child { border-bottom: none; }
"""


def get_js() -> str:
    return """
// ── Вкладки ──────────────────────────────────────────
function showTab(id) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  const idx = ['comparison','stats','adv-stats'].indexOf(id);
  document.querySelectorAll('.tab')[idx].classList.add('active');
}
// ── Поиск ────────────────────────────────────────────
function applySearch() {
  applyFiltersAndSearch();
}

function applyFilters() {
  applyFiltersAndSearch();
}

function applyFiltersAndSearch() {
  const query = (document.getElementById('search-input')?.value || '').toLowerCase().trim();

  document.querySelectorAll('#comparison-table tbody tr').forEach(row => {
    const col0 = row.cells[0]?.textContent.toLowerCase() || '';
    const col1 = row.cells[1]?.textContent.toLowerCase() || '';
    const matchSearch = !query || col0.includes(query) || col1.includes(query);
    const matchFilter = activeFilters.size === 0 || activeFilters.has(row.dataset.color);
    row.style.display = matchSearch && matchFilter ? '' : 'none';
  });
}
// ── Фильтры ──────────────────────────────────────────
const activeFilters = new Set();

function toggleFilter(color, btn) {
  if (activeFilters.has(color)) {
    activeFilters.delete(color);
    btn.classList.remove('active');
  } else {
    activeFilters.add(color);
    btn.classList.add('active');
  }
  applyFilters();
}




// ── Сортировка ───────────────────────────────────────
const sortState = {};

function sortTable(colIdx) {
  const tbody = document.querySelector('#comparison-table tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const asc = !sortState[colIdx];
  sortState[colIdx] = asc;

  rows.sort((a, b) => {
    const va = a.cells[colIdx]?.dataset.val ?? a.cells[colIdx]?.textContent ?? '';
    const vb = b.cells[colIdx]?.dataset.val ?? b.cells[colIdx]?.textContent ?? '';
    const na = parseFloat(va), nb = parseFloat(vb);
    if (!isNaN(na) && !isNaN(nb)) return asc ? na - nb : nb - na;
    return asc ? va.localeCompare(vb, 'ru') : vb.localeCompare(va, 'ru');
  });

  rows.forEach(r => tbody.appendChild(r));

  document.querySelectorAll('#comparison-table th .sort-icon').forEach((icon, i) => {
    icon.textContent = i === colIdx ? (asc ? '▲' : '▼') : '⇅';
  });
}

// ── Навигация к карточке номера ───────────────────────
function openRecord(idx) {
  document.getElementById('comparison-table-wrap').style.display = 'none';
  document.getElementById('comparison-filters').style.display = 'none';
  document.getElementById('search-input').style.display = 'none';
  document.querySelectorAll('.record-card').forEach(c => c.style.display = 'none');
  const card = document.getElementById('record-' + idx);
  if (card) card.style.display = 'block';
}

function backToTable() {
  document.querySelectorAll('.record-card').forEach(c => c.style.display = 'none');
  document.getElementById('comparison-table-wrap').style.display = 'block';
  document.getElementById('comparison-filters').style.display = 'flex';
  document.getElementById('search-input').style.display = 'block';
}

// ── Модал для эталона ─────────────────────────────────
function openModal(el, idx) {
  const row = el.closest('tr');
  const etalon = el.textContent.trim();
  const matches = window.__etalonModalData[etalon];
  if (!matches) return;
  document.getElementById('modal-content').innerHTML =
    '<div class="modal-title">' + etalon + '</div>' +
    matches.map(m =>
      '<div class="modal-item"><span class="link" onclick="openRecord(' + m.idx + ')">' +
      m.recognized + '</span></div>'
    ).join('');
  document.getElementById('modal').classList.add('open');
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
}

// ── Переход на таблицу с фильтром ─────────────────────
function switchToFilter(color) {
  showTab('comparison');
  // сбрасываем все фильтры
  activeFilters.clear();
  document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
  // включаем нужный
  activeFilters.add(color);
  const btnMap = { green: 0, yellow: 1, red: 2, gray: 3 };
  const btns = document.querySelectorAll('.filter-btn');
  if (btns[btnMap[color]]) btns[btnMap[color]].classList.add('active');
  applyFiltersAndSearch();
}

// ── Модал повторов ────────────────────────────────────
function openDuplicatesModal(data) {
  window.__duplicatesData = data;
  const content = document.getElementById('modal-content');
  let html = '<div class="modal-title">Повторы</div>';
  Object.entries(data).forEach(function([etalon, matches]) {
    html += '<div class="modal-item"><span class="link" onclick="openEtalonInModal(this.dataset.etalon)" data-etalon="' + etalon + '">' + etalon + ' (' + matches.length + ')</span></div>';
  });
  content.innerHTML = html;
  document.getElementById('modal').classList.add('open');
}

function openEtalonInModal(etalon) {
  closeModal();
  showTab('comparison');
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.value = etalon;
    applyFiltersAndSearch();
  }
}
function searchEtalon(etalon) {
  showTab('comparison');
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.value = etalon;
    applyFiltersAndSearch();
  }
}

"""
