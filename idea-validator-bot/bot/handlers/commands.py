from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import main_menu
from bot.keyboards.reply import start_keyboard
from bot.services.database import Database

router = Router()


@router.message(F.text.in_(["/start", "🆕 Новая идея"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Привет! Я Валидатор идей.</b>\n\n"
        "Проверь свою идею за пару минут и пойми — стоит ли её развивать.\n\n"
        "📝 Как это работает:\n"
        "1. Введи название идеи\n"
        "2. Добавь аргументы ЗА и ПРОТИВ\n"
        "3. Получи автоматический вердикт\n\n"
        "Сильные идеи проходят проверку.\n"
        "Слабые — ломаются на аргументах.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


@router.message(F.text == "📜 Мои идеи")
async def cmd_my_ideas(message: Message, state: FSMContext, db: Database):
    from bot.handlers.history import show_ideas_list
    await show_ideas_list(message, db)


@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "❓ <b>Помощь</b>\n\n"
        "🆕 <b>Новая идея</b> — начать валидацию с нуля\n"
        "📜 <b>Мои идеи</b> — список всех сохранённых идей\n"
        "➕ <b>ЗА / ПРОТИВ</b> — добавить аргумент\n"
        "✅ <b>Вердикт</b> — увидеть результат анализа\n"
        "📥 <b>Скачать</b> — экспорт в TXT или JSON\n"
        "📤 <b>Поделиться</b> — отправить другу\n\n"
        "💡 Совет: указывай вес аргументов — это делает вердикт точнее!",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


@router.message(F.text == "⬅️ Назад")
async def cmd_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выбери действие:",
        reply_markup=main_menu(),
    )
