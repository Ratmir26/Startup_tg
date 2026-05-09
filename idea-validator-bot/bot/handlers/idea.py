from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import IdeaCreation
from bot.keyboards.inline import main_menu
from bot.services.database import Database
from bot.utils.formatting import format_idea_summary
from bot.utils.safe_edit import safe_edit_text

router = Router()


@router.callback_query(F.data == "new_idea")
async def start_new_idea(callback: CallbackQuery, state: FSMContext, db: Database):
    await state.clear()
    await state.set_state(IdeaCreation.waiting_for_title)
    await safe_edit_text(
        callback.message,
        "✍️ Введи название своей идеи (до 150 символов):",
        reply_markup=None,
    )
    await callback.answer()


@router.message(IdeaCreation.waiting_for_title)
async def save_idea_title(message: Message, state: FSMContext, db: Database):
    title = message.text.strip()
    if not title:
        await message.answer("⚠️ Название не может быть пустым. Попробуй ещё раз:")
        return
    if len(title) > 150:
        await message.answer("⚠️ Название слишком длинное (макс. 150 символов). Сократи:")
        return

    user = await db.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    idea = await db.create_idea(user.id, title)

    await state.update_data(idea_id=idea.id)
    await state.set_state(None)

    await message.answer(
        f"✅ Идея «<b>{title}</b>» сохранена!\n\n"
        f"Теперь добавляй аргументы ЗА и ПРОТИВ:",
        reply_markup=main_menu(idea_id=idea.id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("back_to_idea:"))
async def back_to_idea(callback: CallbackQuery, state: FSMContext, db: Database):
    await state.clear()
    idea_id = callback.data.split(":", 1)[1]
    result = await db.get_idea_full(idea_id)
    if not result:
        await callback.answer("❌ Идея не найдена")
        return

    idea, pros, cons = result
    text = format_idea_summary(idea, pros, cons)
    await safe_edit_text(
        callback.message,
        text,
        reply_markup=main_menu(idea_id=idea.id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit_text(
        callback.message,
        "Выбери действие:",
        reply_markup=main_menu(),
    )
    await callback.answer()
