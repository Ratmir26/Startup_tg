from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states import IdeaCreation
from bot.services.database import Database
from bot.keyboards.inline import argument_action_keyboard, weight_keyboard, main_menu
from bot.utils.formatting import format_idea_summary
from bot.utils.safe_edit import safe_edit_text

router = Router()


@router.callback_query(F.data.startswith("add_pro:"))
@router.callback_query(F.data.startswith("add_con:"))
async def start_add_argument(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    action = parts[0]
    idea_id = parts[1]
    arg_type = "pro" if action == "add_pro" else "con"

    await state.update_data(idea_id=idea_id, arg_type=arg_type)
    await state.set_state(IdeaCreation.waiting_for_argument_text)

    type_word = "ЗА" if arg_type == "pro" else "ПРОТИВ"
    await safe_edit_text(
        callback.message,
        f"✍️ Введи аргумент {type_word} (мин. 3 символа):",
        reply_markup=None,
    )
    await callback.answer()


@router.message(IdeaCreation.waiting_for_argument_text)
async def save_argument_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 3:
        await message.answer("⚠️ Аргумент слишком короткий (мин. 3 символа). Попробуй ещё раз:")
        return

    await state.update_data(arg_text=text)
    await state.set_state(IdeaCreation.waiting_for_argument_weight)

    data = await state.get_data()
    idea_id = data.get("idea_id")
    arg_type = data.get("arg_type")

    await message.answer(
        "Выбери вес аргумента:",
        reply_markup=weight_keyboard(idea_id, arg_type),
    )


@router.callback_query(F.data.startswith("weight:"))
async def save_argument_weight(callback: CallbackQuery, state: FSMContext, db: Database):
    parts = callback.data.split(":")
    idea_id = parts[1]
    arg_type = parts[2]
    weight = parts[3]

    data = await state.get_data()
    arg_text = data.get("arg_text")

    await db.add_argument(idea_id, arg_type, arg_text, weight)

    await state.clear()

    result = await db.get_idea_full(idea_id)
    if not result:
        await callback.answer("❌ Ошибка")
        return

    idea, pros, cons = result
    text = format_idea_summary(idea, pros, cons)

    await safe_edit_text(
        callback.message,
        f"✅ Аргумент добавлен!\n\n{text}",
        reply_markup=main_menu(idea_id=idea.id),
        parse_mode="HTML",
    )
    await callback.answer("✅ Добавлено!")


@router.callback_query(F.data.startswith("verdict:"))
async def show_verdict(callback: CallbackQuery, db: Database):
    from bot.keyboards.inline import verdict_keyboard
    from bot.services.validator import get_verdict, make_progress_bar

    idea_id = callback.data.split(":", 1)[1]
    result = await db.get_idea_full(idea_id)
    if not result:
        await callback.answer("❌ Идея не найдена")
        return

    idea, pros, cons = result
    verdict = get_verdict(pros, cons)
    bar = make_progress_bar(verdict.percent)

    pro_list = ""
    for i, a in enumerate(pros, 1):
        w = {"weak": "🔴", "medium": "🟡", "strong": "🟢"}.get(a.weight, "🟡")
        pro_list += f"{i}. {w} {a.text}\n"

    con_list = ""
    for i, a in enumerate(cons, 1):
        w = {"weak": "🔴", "medium": "🟡", "strong": "🟢"}.get(a.weight, "🟡")
        con_list += f"{i}. {w} {a.text}\n"

    text = (
        f"📊 <b>Вердикт для «{idea.title}»</b>\n\n"
        f"<b>ЗА ({len(pros)}):</b>\n{pro_list if pro_list else '(пусто)\n'}"
        f"<b>ПРОТИВ ({len(cons)}):</b>\n{con_list if con_list else '(пусто)\n'}"
        f"\n{bar} {verdict.percent}%\n\n"
        f"<b>{verdict.text}</b>\n"
        f"Score: {'+' if verdict.score > 0 else ''}{verdict.score} | Статус: {verdict.confidence}"
    )

    await safe_edit_text(
        callback.message,
        text,
        reply_markup=verdict_keyboard(idea_id),
        parse_mode="HTML",
    )
    await callback.answer()
