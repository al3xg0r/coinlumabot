# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Основные настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Настройки путей и файлов
LOG_FILE = "bot.log"
USER_LANGS_FILE = "user_langs.json"

# API настройки
# 1. CoinGecko
COINGECKO_URL = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

# 2. CoinMarketCap (Новый)
COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1"
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "")

# 3. Резервные
COINCAP_URL = "https://api.coincap.io/v2"
CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/price"