import os
import re

# =========================
# НАСТРОЙКИ
# =========================

CONFIG_DIR = r"C:\ProgramData\ISS\logs\modules\auto"

# что извлекаем (расширяемо)
SEARCH_PATTERNS = {
    "max_height_symbol": r"<filter_max_symbol_height>(.*?)</filter_max_symbol_height>",
    "min_height_symbol": r"<filter_min_symbol_height>(.*?)</filter_min_symbol_height>",
    "same_number_time": r"<filter_same_number>(.*?)</filter_same_number>",
    "quality": r"<filter_quality>(.*?)</filter_quality>",
    "mode" : r"<single_frame_mode>(.*?)</single_frame_mode>",
    "tracking_mode": r"<tracking_mode>(.*?)</tracking_mode>",
}


# =========================
# ПРОВЕРКА СОВПАДЕНИЯ
# =========================
def match_keywords(content, keywords):
    matches = []

    for word in keywords:
        if word.lower() in content.lower():
            matches.append(word)

    return matches


# =========================
# ИЗВЛЕЧЕНИЕ ПАРАМЕТРОВ
# =========================
def extract_parameters(content):
    extracted = {}

    for param_name, pattern in SEARCH_PATTERNS.items():
        match = re.search(pattern, content)
        if match:
            extracted[param_name] = match.group(1)

    return extracted


# =========================
# ОСНОВНАЯ ФУНКЦИЯ
# =========================
def get_settings(keywords: list[str]):
    results = []

    if not keywords:
        return results

    if not os.path.exists(CONFIG_DIR):
        return results

    for filename in os.listdir(CONFIG_DIR):

        if not filename.startswith("autoi_cam_root"):
            continue

        file_path = os.path.join(CONFIG_DIR, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            # читаем файл
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except:
                with open(file_path, "r", encoding="cp1251") as f:
                    content = f.read()

            # ищем совпадения
            matched_words = match_keywords(content, keywords)

            if not matched_words:
                continue

            # извлекаем параметры
            params = extract_parameters(content)

            if not params:
                continue

            results.append({
                "file": filename,
                "matched_keywords": matched_words,
                "params": params
            })

        except:
            continue

    return results