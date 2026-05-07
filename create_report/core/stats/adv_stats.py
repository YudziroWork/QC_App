from collections import Counter
from create_report.config.settings import THRESHOLD


def calculate_advanced_statistics(results: list) -> dict:
    etalon_usage = Counter()
    error_stats = Counter()

    for item in results:
        best = item["best_match"]
        dist = item["distance"]

        if not best or item.get("no_number", False):
            continue

        recognized = item["recognized"]
        threshold = THRESHOLD * len(best)

        if dist == 0:
            etalon_usage[best] += 1
        elif dist < threshold:
            etalon_usage[best] += 1

            # анализ ошибок посимвольно
            min_len = min(len(best), len(recognized))
            for i in range(min_len):
                if best[i] != recognized[i]:
                    error_stats[f"{recognized[i]} → {best[i]}"] += 1

            if len(recognized) != len(best):
                error_stats["Длина отличается"] += 1

    return {
        "etalon_usage": dict(etalon_usage),
        "error_stats": dict(error_stats),
    }