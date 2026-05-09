import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import BOT_TOKEN, DATABASE_URL, WEBAPP_URL
from bot.services.database import Database

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
bot_db = Database(DATABASE_URL)


class DatabaseMiddleware:
    async def __call__(self, handler, event, data):
        data["db"] = bot_db
        return await handler(event, data)


async def set_commands():
    commands = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)


def register_handlers():
    from bot.handlers.commands import router as commands_router
    from bot.handlers.idea import router as idea_router
    from bot.handlers.arguments import router as arguments_router
    from bot.handlers.history import router as history_router
    from bot.handlers.export import router as export_router
    from bot.handlers.hypothesis import router as hypothesis_router

    dp.include_router(commands_router)
    dp.include_router(idea_router)
    dp.include_router(arguments_router)
    dp.include_router(history_router)
    dp.include_router(export_router)
    dp.include_router(hypothesis_router)


@dp.startup()
async def on_startup(bot: Bot):
    await bot_db.init_db()
    await set_commands()
    logging.info("Бот запущен!")


@dp.shutdown()
async def on_shutdown(bot: Bot):
    logging.info("Бот остановлен.")


async def main():
    dp.update.middleware(DatabaseMiddleware())
    register_handlers()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
