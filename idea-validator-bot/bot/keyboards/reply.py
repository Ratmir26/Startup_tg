from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Новая идея"), KeyboardButton(text="📜 Мои идеи")],
            [KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
    )
