import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required! Set it in .env file.")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/bot.db")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com/webapp/")
