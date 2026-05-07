
from create_report.config.settings import THRESHOLD


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    d = {}
    len1 = len(s1)
    len2 = len(s2)

    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,
                d[(i, j - 1)] + 1,
                d[(i - 1, j - 1)] + cost
            )
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + cost)

    return d[(len1 - 1, len2 - 1)]


def normalize(value: str) -> str:
    return str(value).strip().upper()


def get_color(distance: int, record_length: int) -> str:
    threshold = THRESHOLD * record_length
    if distance == 0:
        return "green"
    elif distance <= threshold:
        return "yellow"
    else:
        return "red"


def compare(etalon: list, report: list) -> tuple[list, dict]:

    etalon_scores = {normalize(e): 0 for e in etalon}

    results = []

    for record in report:
        number = normalize(record["number"])
        time = record["time"]

        # пропускаем записи без номера
        if number == "" or number == "НЕТ НОМЕРА":
            results.append({
                "recognized": number,
                "time": time,
                "best_match": None,
                "distance": None,
                "color": "red",
                "no_number": True
            })
            continue

        # ищем ближайший эталон
        best_match = None
        min_distance = float("inf")

        for e in etalon:
            e_norm = normalize(e)
            dist = damerau_levenshtein_distance(number, e_norm)
            if dist < min_distance:
                min_distance = dist
                best_match = e_norm

        color = get_color(min_distance, len(number))

        # начисляем балл эталону если совпадение не красное
        if color != "red" and best_match in etalon_scores:
            etalon_scores[best_match] += 1

        results.append({
            "recognized": number,
            "time": time,
            "best_match": best_match,
            "distance": min_distance,
            "color": color,
            "no_number": False
        })

    # сортировка по времени
    results.sort(key=lambda r: r["time"])
    # считаем статистику


    return results


