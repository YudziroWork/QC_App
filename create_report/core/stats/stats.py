from collections import Counter

def calculate_statistics(results: list, etalon_list: list, threshold_ratio: float = 0.55) -> dict:
    total = len(results)
    fully = 0
    partial = 0
    incorrect = 0
    without_number = 0

    best_matches_for_duplicates = []
    missed = []

    for item in results:
        # проверка на "нет номера"
        if item.get("no_number", False):
            without_number += 1
            continue

        dist = item["distance"]
        best = item["best_match"]
        number = item["recognized"]
        threshold = threshold_ratio * len(number)

        if best:
            if dist == 0:
                fully += 1
                best_matches_for_duplicates.append(best)
            elif dist < threshold:
                partial += 1
                best_matches_for_duplicates.append(best)
            else:
                incorrect += 1
        else:
            incorrect += 1

    # повторы: считаем сколько раз каждый эталон встречается сверх первого
    counter = Counter(best_matches_for_duplicates)
    duplicates_count = sum(count - 1 for count in counter.values() if count > 1)

    # пропуски
    total_etalon = len(etalon_list)
    not_used_count = total_etalon - (fully + partial - duplicates_count)

    # список пропущенных номеров эталона
    used_etalon = set(best_matches_for_duplicates)
    missed = [e for e in etalon_list if e not in used_etalon]

    # precision/recall/F1
    # защита от деления на ноль
    def safe_div(a, b):
        return a / b if b else 0.0

    precision_strict = safe_div(fully, fully + duplicates_count + incorrect)
    recall_strict    = safe_div(fully, fully + not_used_count)
    f1_strict        = safe_div(2 * fully, 2 * fully + duplicates_count + incorrect + not_used_count)

    precision_soft = safe_div(fully + partial, fully + partial + duplicates_count + incorrect)
    recall_soft    = safe_div(fully + partial, fully + partial + not_used_count)
    f1_soft        = safe_div(2 * (fully + partial), 2 * (fully + partial) + duplicates_count + incorrect + not_used_count)

    return {
        # основная статистика
        "total":           total,
        "fully":           fully,
        "partial":         partial,
        "incorrect":       incorrect,
        "without_number":  without_number,
        "duplicates":      duplicates_count,
        # статистика эталона
        "etalon_total":    total_etalon,
        "etalon_found":    total_etalon - not_used_count,
        "missed_count":    not_used_count,
        "missed":          missed,
        # качество strict
        "precision_strict": round(precision_strict * 100, 2),
        "recall_strict":    round(recall_strict * 100, 2),
        "f1_strict":        round(f1_strict * 100, 2),
        # качество soft
        "precision_soft":   round(precision_soft * 100, 2),
        "recall_soft":      round(recall_soft * 100, 2),
        "f1_soft":          round(f1_soft * 100, 2),
    }