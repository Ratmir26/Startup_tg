from dataclasses import dataclass

WEIGHT_VALUES = {"weak": 1, "medium": 2, "strong": 3}


@dataclass
class VerdictResult:
    text: str
    cls: str
    score: int
    confidence: str
    key: str
    pro_weighted: int
    con_weighted: int
    total: int
    percent: int


def get_verdict(pros: list, cons: list) -> VerdictResult:
    pro_weighted = sum(WEIGHT_VALUES.get(a.weight, 2) for a in pros)
    con_weighted = sum(WEIGHT_VALUES.get(a.weight, 2) for a in cons)
    total = len(pros) + len(cons)
    score = pro_weighted - con_weighted
    total_weighted = pro_weighted + con_weighted
    percent = round((pro_weighted / total_weighted) * 100) if total_weighted > 0 else 50

    if total == 0:
        return VerdictResult("🤔 Добавь аргументы", "neutral", score, "Нет данных", "uncertain", pro_weighted, con_weighted, total, percent)
    if total < 3:
        return VerdictResult("🤔 Нужно больше данных", "neutral", score, "Мало данных", "uncertain", pro_weighted, con_weighted, total, percent)
    if pro_weighted > con_weighted * 1.5:
        return VerdictResult("🚀 Идея перспективная!", "positive", score, "Достаточно данных", "promising", pro_weighted, con_weighted, total, percent)
    if con_weighted > pro_weighted * 1.5:
        return VerdictResult("❌ Идея слабая", "negative", score, "Достаточно данных", "weak", pro_weighted, con_weighted, total, percent)
    if score > 0:
        conf = "Достаточно данных" if total >= 5 else "Мало данных"
        return VerdictResult("👍 Скорее перспективная", "positive", score, conf, "promising", pro_weighted, con_weighted, total, percent)
    if score < 0:
        conf = "Достаточно данных" if total >= 5 else "Мало данных"
        return VerdictResult("👎 Скорее слабая", "negative", score, conf, "weak", pro_weighted, con_weighted, total, percent)
    return VerdictResult("⚖️ Равновесие", "neutral", score, "Нужно больше аргументов", "uncertain", pro_weighted, con_weighted, total, percent)


def make_progress_bar(percent: int, length: int = 10) -> str:
    filled = round(percent / 100 * length)
    filled = max(0, min(length, filled))
    empty = length - filled
    return "█" * filled + "░" * empty
