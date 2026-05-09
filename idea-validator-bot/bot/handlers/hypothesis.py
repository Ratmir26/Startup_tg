from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states import HypothesisSurvey
from bot.services.database import Database
from bot.keyboards.inline import hypothesis_question_keyboard, survey_result_keyboard, main_menu
from bot.utils.safe_edit import safe_edit_text
from bot.utils.formatting import escape_html

router = Router()


@router.callback_query(F.data.startswith("start_survey:"))
async def start_survey(callback: CallbackQuery, state: FSMContext, db: Database):
    idea_id = callback.data.split(":", 1)[1]
    idea = await db.get_idea(idea_id)
    if not idea:
        await callback.answer("❌ Идея не найдена")
        return

    await state.clear()
    await state.update_data(idea_id=idea_id, idea_title=idea.title)
    await state.set_state(HypothesisSurvey.waiting_for_audience)

    await safe_edit_text(
        callback.message,
        f"📋 <b>Опрос гипотезы</b>\n\n"
        f"Идея: <b>{escape_html(idea.title)}</b>\n\n"
        f"Шаг 1/5: <b>Кто целевая аудитория?</b>\n"
        f"Напиши, на кого рассчитана твоя идея.\n"
        f"Например: школьники 14-18 лет",
        reply_markup=None,
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(HypothesisSurvey.waiting_for_audience)
async def process_audience(message: Message, state: FSMContext):
    audience = message.text.strip()
    if not audience:
        await message.answer("⚠️ Напиши целевую аудиторию. Например: школьники 14-18 лет")
        return
    if len(audience) > 200:
        await message.answer("⚠️ Слишком длинный текст (макс. 200 символов). Сократи:")
        return

    await state.update_data(audience=audience)
    await state.set_state(HypothesisSurvey.waiting_for_frequency)

    data = await state.get_data()
    await message.answer(
        f"📋 <b>Шаг 2/5: Как часто возникает проблема?</b>\n\n"
        f"Выбери вариант:",
        reply_markup=hypothesis_question_keyboard("frequency", data["idea_id"]),
        parse_mode="HTML",
    )


async def process_survey_answer(callback: CallbackQuery, state: FSMContext, step: str, value: int, idea_id: str, next_state, next_label: str, next_question: str, next_keyboard_step: str):
    data = await state.get_data()
    saved_idea_id = data.get("idea_id")
    if saved_idea_id != idea_id:
        await callback.answer("❌ Ошибка: идея изменилась")
        return

    answers = data.get("answers", {})
    answers[step] = value
    await state.update_data(answers=answers)
    await state.set_state(next_state)

    kb = hypothesis_question_keyboard(next_keyboard_step, idea_id) if next_keyboard_step else None
    await safe_edit_text(
        callback.message,
        f"📋 <b>{next_label}</b>\n\n{next_question}",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


SURVEY_STEPS = [
    ("frequency", HypothesisSurvey.waiting_for_payment, "Шаг 3/5: Готовность платить", "Готовы ли твои клиенты платить за решение?", "payment"),
    ("payment", HypothesisSurvey.waiting_for_competitors, "Шаг 4/5: Конкуренты", "Сколько конкурентов на рынке?", "competitors"),
    ("competitors", HypothesisSurvey.waiting_for_testability, "Шаг 5/5: Проверка гипотезы", "Можно ли проверить идею за неделю?", "test"),
]


@router.callback_query(F.data.startswith("survey_ans:frequency:"))
async def process_frequency(callback: CallbackQuery, state: FSMContext, db: Database):
    parts = callback.data.split(":")
    value = int(parts[2])
    idea_id = parts[3]
    step_info = SURVEY_STEPS[0]
    await process_survey_answer(
        callback, state, "frequency", value, idea_id,
        step_info[1], step_info[2], step_info[3], step_info[4],
    )


@router.callback_query(F.data.startswith("survey_ans:payment:"))
async def process_payment(callback: CallbackQuery, state: FSMContext, db: Database):
    parts = callback.data.split(":")
    value = int(parts[2])
    idea_id = parts[3]
    step_info = SURVEY_STEPS[1]
    await process_survey_answer(
        callback, state, "payment", value, idea_id,
        step_info[1], step_info[2], step_info[3], step_info[4],
    )


@router.callback_query(F.data.startswith("survey_ans:competitors:"))
async def process_competitors(callback: CallbackQuery, state: FSMContext, db: Database):
    parts = callback.data.split(":")
    value = int(parts[2])
    idea_id = parts[3]
    step_info = SURVEY_STEPS[2]
    await process_survey_answer(
        callback, state, "competitors", value, idea_id,
        step_info[1], step_info[2], step_info[3], step_info[4],
    )


@router.callback_query(F.data.startswith("survey_ans:test:"))
async def process_testability(callback: CallbackQuery, state: FSMContext, db: Database):
    parts = callback.data.split(":")
    value = int(parts[2])
    idea_id = parts[3]

    data = await state.get_data()
    saved_idea_id = data.get("idea_id")
    if saved_idea_id != idea_id:
        await callback.answer("❌ Ошибка: идея изменилась")
        return

    answers = data.get("answers", {})
    answers["test"] = value
    await state.update_data(answers=answers)

    result = calculate_survey_result(answers, data.get("audience", ""))
    await show_survey_result(callback.message, result, idea_id)
    await state.clear()
    await callback.answer()


def calculate_survey_result(answers: dict, audience: str) -> dict:
    names = ["frequency", "payment", "competitors", "test"]
    base = 4
    max_score = 20
    actual = base + sum(answers.get(n, 0) for n in names)
    actual = min(actual, max_score)
    percent = round((actual / max_score) * 100)

    if actual >= 16:
        emoji, text, color = "🚀", "Отличная идея для проверки!", "green"
    elif actual >= 11:
        emoji, text, color = "👍", "Хорошая идея, но есть вопросы", "orange"
    elif actual >= 6:
        emoji, text, color = "⚠️", "Нужно больше исследований", "orange"
    else:
        emoji, text, color = "🛑", "Пока рано, доработай идею", "red"

    filled = round(percent / 100 * 10)
    bar = "█" * filled + "░" * (10 - filled)

    return {
        "emoji": emoji,
        "text": text,
        "color": color,
        "actual": actual,
        "max": max_score,
        "percent": percent,
        "bar": bar,
        "audience": audience or "—",
    }


async def show_survey_result(message: Message, result: dict, idea_id: str):
    color_map = {"green": "✅", "orange": "⚠️", "red": "❌"}
    icon = color_map.get(result["color"], "❓")

    await safe_edit_text(
        message,
        f"📋 <b>Результат опроса гипотезы</b>\n\n"
        f"{result['bar']} {result['percent']}%\n\n"
        f"<b>{result['emoji']} {result['text']}</b>\n\n"
        f"{icon} Оценка: <b>{result['actual']}/{result['max']}</b>\n"
        f"👥 ЦА: <i>{escape_html(result['audience'])}</i>\n\n"
        f"Проверь гипотезу на реальных пользователях!",
        reply_markup=survey_result_keyboard(idea_id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("cancel_survey:"))
async def cancel_survey(callback: CallbackQuery, state: FSMContext, db: Database):
    idea_id = callback.data.split(":", 1)[1]
    await state.clear()

    result = await db.get_idea_full(idea_id)
    if result:
        idea, pros, cons = result
        from bot.utils.formatting import format_idea_summary
        text = format_idea_summary(idea, pros, cons)
        await safe_edit_text(
            callback.message,
            text,
            reply_markup=main_menu(idea_id=idea.id),
            parse_mode="HTML",
        )
    else:
        await safe_edit_text(
            callback.message,
            "Опрос отменён",
            reply_markup=main_menu(),
        )
    await callback.answer()
