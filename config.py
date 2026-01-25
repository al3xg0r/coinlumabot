# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Получаем данные (если их нет, вернется None)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Преобразуем ID в число, если оно было считано
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

# Пути к файлам
LOG_FILE = "bot_log.log"
USER_LANGS_FILE = "data/user_langs.json"

# API URLS
COINGECKO_URL = "https://api.coingecko.com/api/v3"
COINCAP_URL = "https://api.coincap.io/v2"