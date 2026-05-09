import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/bot.db")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com/webapp/")
