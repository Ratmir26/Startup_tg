import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def safe_edit_text(message: Message, text: str, **kwargs):
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        if "not modified" in str(e).lower():
            pass
        elif "message is not modified" in str(e).lower():
            pass
        else:
            await message.answer(text, **kwargs)
