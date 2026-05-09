def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_verdict_message(idea_title: str, pros: list, cons: list, verdict) -> str:
    from bot.services.validator import make_progress_bar

    bar = make_progress_bar(verdict.percent)

    pro_list = ""
    for i, a in enumerate(pros, 1):
        weight_emoji = {"weak": "🔴", "medium": "🟡", "strong": "🟢"}.get(a.weight, "🟡")
        pro_list += f"{i}. {weight_emoji} {escape_html(a.text)}\n"

    con_list = ""
    for i, a in enumerate(cons, 1):
        weight_emoji = {"weak": "🔴", "medium": "🟡", "strong": "🟢"}.get(a.weight, "🟡")
        con_list += f"{i}. {weight_emoji} {escape_html(a.text)}\n"

    msg = (
        f"📊 <b>Вердикт для «{escape_html(idea_title)}»</b>\n\n"
        f"<b>ЗА ({len(pros)}):</b>\n{pro_list if pro_list else '(пусто)\n'}"
        f"<b>ПРОТИВ ({len(cons)}):</b>\n{con_list if con_list else '(пусто)\n'}"
        f"\n{bar} {verdict.percent}%\n\n"
        f"<b>{verdict.text}</b>\n"
        f"Score: {'+' if verdict.score > 0 else ''}{verdict.score} | Статус: {verdict.confidence}"
    )
    return msg


def format_idea_list_item(idea, pros: int, cons: int, verdict_key: str) -> str:
    emoji = {"promising": "🚀", "weak": "❌", "uncertain": "⚖️"}.get(verdict_key, "🤔")
    date_str = idea.updated_at.strftime("%d.%m, %H:%M") if idea.updated_at else idea.created_at.strftime("%d.%m, %H:%M")
    return f"{emoji} {escape_html(idea.title)} <i>({date_str})</i> — ЗА:{pros} ПРОТИВ:{cons}"


def format_idea_summary(idea, pros: list, cons: list) -> str:
    from bot.services.validator import get_verdict, make_progress_bar

    verdict = get_verdict(pros, cons)
    bar = make_progress_bar(verdict.percent)

    msg = (
        f"📝 <b>{escape_html(idea.title)}</b>\n\n"
        f"ЗА: {len(pros)} | ПРОТИВ: {len(cons)} | Score: {'+' if verdict.score > 0 else ''}{verdict.score}\n"
        f"{bar} {verdict.percent}%\n\n"
        f"{verdict.text}\n"
        f"Статус: {verdict.confidence}"
    )
    return msg
