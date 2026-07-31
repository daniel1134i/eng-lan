import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = os.getenv("DB_PATH", "bot.sqlite3")

if not BOT_TOKEN and os.path.exists(".env"):
    print("Warning: BOT_TOKEN is empty in .env file.")
