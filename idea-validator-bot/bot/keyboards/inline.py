from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import WEBAPP_URL


def main_menu(idea_id: str = None) -> InlineKeyboardMarkup:
    buttons = []
    if idea_id:
        buttons.append([
            InlineKeyboardButton(text="➕ ЗА", callback_data=f"add_pro:{idea_id}"),
            InlineKeyboardButton(text="➖ ПРОТИВ", callback_data=f"add_con:{idea_id}"),
        ])
        buttons.append([
            InlineKeyboardButton(text="✅ Вердикт", callback_data=f"verdict:{idea_id}"),
            InlineKeyboardButton(text="🔍 Опрос", callback_data=f"start_survey:{idea_id}"),
        ])
        buttons.append([
            InlineKeyboardButton(text="🆕 Новая идея", callback_data="new_idea"),
            InlineKeyboardButton(text="📜 Мои идеи", callback_data="list_ideas"),
        ])
        buttons.append([
            InlineKeyboardButton(text="🖥 Открыть в приложении", web_app={"url": WEBAPP_URL}),
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="🆕 Новая идея", callback_data="new_idea"),
        ])
        buttons.append([
            InlineKeyboardButton(text="📜 Мои идеи", callback_data="list_ideas"),
        ])
        buttons.append([
            InlineKeyboardButton(text="🖥 Открыть в приложении", web_app={"url": WEBAPP_URL}),
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def argument_action_keyboard(idea_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Ещё ЗА", callback_data=f"add_pro:{idea_id}"),
            InlineKeyboardButton(text="➖ Ещё ПРОТИВ", callback_data=f"add_con:{idea_id}"),
        ],
        [
            InlineKeyboardButton(text="✅ Вердикт", callback_data=f"verdict:{idea_id}"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_idea:{idea_id}"),
        ],
    ])


def weight_keyboard(idea_id: str, arg_type: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Слабый", callback_data=f"weight:{idea_id}:{arg_type}:weak"),
        ],
        [
            InlineKeyboardButton(text="🟡 Средний", callback_data=f"weight:{idea_id}:{arg_type}:medium"),
        ],
        [
            InlineKeyboardButton(text="🟢 Сильный", callback_data=f"weight:{idea_id}:{arg_type}:strong"),
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data=f"back_to_idea:{idea_id}"),
        ],
    ])


def hypothesis_question_keyboard(step: str, idea_id: str) -> InlineKeyboardMarkup:
    options = {
        "frequency": [
            ("🔴 Редко", "1"),
            ("🟡 Иногда", "2"),
            ("🟢 Часто", "3"),
            ("💚 Постоянно", "4"),
        ],
        "payment": [
            ("🔴 Не готовы", "1"),
            ("🟡 Немногие готовы", "2"),
            ("🟢 Большинство готовы", "3"),
            ("💚 Однозначно готовы", "4"),
        ],
        "competitors": [
            ("💚 Конкурентов нет", "4"),
            ("🟢 Мало конкурентов", "3"),
            ("🟡 Есть конкуренция", "2"),
            ("🔴 Высокая конкуренция", "1"),
        ],
        "test": [
            ("💚 Легко проверить", "4"),
            ("🟢 Можно проверить", "3"),
            ("🟡 Сложно проверить", "2"),
            ("🔴 Невозможно проверить", "1"),
        ],
    }
    btns = [[InlineKeyboardButton(text=label, callback_data=f"survey_ans:{step}:{val}:{idea_id}")] for label, val in options.get(step, [])]
    btns.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_survey:{idea_id}")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def survey_result_keyboard(idea_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти ещё раз", callback_data=f"start_survey:{idea_id}")],
        [InlineKeyboardButton(text="⬅️ К идее", callback_data=f"back_to_idea:{idea_id}")],
    ])


def verdict_keyboard(idea_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📥 Скачать TXT", callback_data=f"export_txt:{idea_id}"),
            InlineKeyboardButton(text="📥 JSON", callback_data=f"export_json:{idea_id}"),
        ],
        [
            InlineKeyboardButton(text="📤 Поделиться", callback_data=f"share:{idea_id}"),
        ],
        [
            InlineKeyboardButton(text="➕ Добавить ещё", callback_data=f"back_to_idea:{idea_id}"),
            InlineKeyboardButton(text="🆕 Новая идея", callback_data="new_idea"),
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить идею", callback_data=f"delete_idea:{idea_id}"),
        ],
    ])


def ideas_list_keyboard(ideas_with_data: list) -> InlineKeyboardMarkup:
    buttons = []
    for i, (idea, pros, cons, verdict_key) in enumerate(ideas_with_data, 1):
        emoji = {"promising": "🚀", "weak": "❌", "uncertain": "⚖️"}.get(verdict_key, "🤔")
        buttons.append([
            InlineKeyboardButton(
                text=f"{i}. {emoji} {idea.title[:30]}",
                callback_data=f"load_idea:{idea.id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🆕 Новая идея", callback_data="new_idea"),
    ])
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_delete_keyboard(idea_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑 Да, удалить", callback_data=f"confirm_delete:{idea_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Нет", callback_data=f"back_to_idea:{idea_id}"),
        ],
    ])
