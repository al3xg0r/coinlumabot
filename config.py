# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Ссылка для Demo API (с ключом)
COINGECKO_URL = "https://api.coingecko.com/api/v3" 
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

COINCAP_URL = "https://api.coincap.io/v2"

# Добавим еще один резерв (не требует ключа для простых запросов)
CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/price"