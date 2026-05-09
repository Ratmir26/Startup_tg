from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.services.database import Database
from bot.services.export import generate_txt, generate_json, save_to_file
from bot.utils.safe_edit import safe_edit_text

router = Router()


@router.callback_query(F.data.startswith("export_txt:"))
async def export_txt(callback: CallbackQuery, db: Database):
    idea_id = callback.data.split(":", 1)[1]
    result = await db.get_idea_full(idea_id)
    if not result:
        await callback.answer("❌ Идея не найдена")
        return

    idea, pros, cons = result
    content = await generate_txt(idea.title, pros, cons)
    filepath = await save_to_file(content, f"validation_{idea_id}.txt")

    with open(filepath, "rb") as f:
        await callback.message.answer_document(
            document=f,
            caption=f"📥 Результат валидации: {idea.title}",
        )

    await callback.answer("📥 TXT готов!")


@router.callback_query(F.data.startswith("export_json:"))
async def export_json(callback: CallbackQuery, db: Database):
    idea_id = callback.data.split(":", 1)[1]
    result = await db.get_idea_full(idea_id)
    if not result:
        await callback.answer("❌ Идея не найдена")
        return

    idea, pros, cons = result
    content = await generate_json(idea.title, pros, cons)
    filepath = await save_to_file(content, f"validation_{idea_id}.json")

    with open(filepath, "rb") as f:
        await callback.message.answer_document(
            document=f,
            caption=f"📥 JSON: {idea.title}",
        )

    await callback.answer("📥 JSON готов!")


@router.callback_query(F.data.startswith("share:"))
async def share_idea(callback: CallbackQuery, db: Database):
    idea_id = callback.data.split(":", 1)[1]
    result = await db.get_idea_full(idea_id)
    if not result:
        await callback.answer("❌ Идея не найдена")
        return

    from bot.services.validator import get_verdict

    idea, pros, cons = result
    verdict = get_verdict(pros, cons)

    text = (
        f"🧠 Валидация идеи: {idea.title}\n"
        f"ЗА: {len(pros)} | ПРОТИВ: {len(cons)} | Score: {'+' if verdict.score > 0 else ''}{verdict.score}\n"
        f"{verdict.text}\n\n"
        f"Проверь и свою идею!"
    )

    await callback.message.answer(
        f"📤 Скопируй и отправь другу:\n\n<code>{text}</code>",
        parse_mode="HTML",
    )
    await callback.answer("📤 Готово!")


@router.callback_query(F.data.startswith("delete_idea:"))
async def prompt_delete(callback: CallbackQuery):
    from bot.keyboards.inline import confirm_delete_keyboard

    idea_id = callback.data.split(":", 1)[1]
    await safe_edit_text(
        callback.message,
        "🗑 Ты точно хочешь удалить эту идею? Это действие нельзя отменить.",
        reply_markup=confirm_delete_keyboard(idea_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete(callback: CallbackQuery, db: Database):
    idea_id = callback.data.split(":", 1)[1]
    idea = await db.get_idea(idea_id)
    if idea:
        await db.delete_idea(idea_id)
        await safe_edit_text(
            callback.message,
            "🗑 Идея удалена.",
            reply_markup=None,
        )
    else:
        await safe_edit_text(
            callback.message,
            "❌ Идея не найдена.",
            reply_markup=None,
        )
    await callback.answer("🗑 Удалено!")
