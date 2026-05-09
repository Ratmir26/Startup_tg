from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.database import Database
from bot.services.validator import get_verdict
from bot.keyboards.inline import ideas_list_keyboard, main_menu
from bot.utils.formatting import format_idea_summary
from bot.utils.safe_edit import safe_edit_text

router = Router()


async def show_ideas_list(message_or_callback, db: Database):
    user_id = message_or_callback.from_user.id

    ideas = await db.get_user_ideas(user_id)
    if not ideas:
        text = "📜 У тебя пока нет идей.\n\nНажми «🆕 Новая идея» чтобы начать!"
        if isinstance(message_or_callback, CallbackQuery):
            await safe_edit_text(message_or_callback.message, text, reply_markup=main_menu())
            await message_or_callback.answer()
        else:
            await message_or_callback.answer(text, reply_markup=main_menu())
        return

    ideas_with_data = []
    for idea in ideas:
        pros, cons = await db.get_idea_arguments(idea.id)
        verdict = get_verdict(pros, cons)
        ideas_with_data.append((idea, len(pros), len(cons), verdict.key))

    kb = ideas_list_keyboard(ideas_with_data)
    text = "📜 <b>Твои идеи:</b>"

    if isinstance(message_or_callback, CallbackQuery):
        await safe_edit_text(message_or_callback.message, text, reply_markup=kb, parse_mode="HTML")
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "list_ideas")
async def cmd_list_ideas(callback: CallbackQuery, state: FSMContext, db: Database):
    await show_ideas_list(callback, db)


@router.callback_query(F.data.startswith("load_idea:"))
async def load_idea(callback: CallbackQuery, state: FSMContext, db: Database):
    idea_id = callback.data.split(":", 1)[1]
    result = await db.get_idea_full(idea_id)
    if not result:
        await callback.answer("❌ Идея не найдена")
        return

    idea, pros, cons = result
    text = format_idea_summary(idea, pros, cons)

    await safe_edit_text(
        callback.message,
        f"✅ Идея загружена!\n\n{text}",
        reply_markup=main_menu(idea_id=idea.id),
        parse_mode="HTML",
    )
    await callback.answer()
