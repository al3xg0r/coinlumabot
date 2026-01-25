# utils.py
import logging
import json
import os
from logging.handlers import RotatingFileHandler
from config import LOG_FILE, USER_LANGS_FILE, ADMIN_ID

# Настройка логирования (макс 3МБ)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=3*1024*1024, backupCount=1),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Работа с языками
def load_user_languages():
    if not os.path.exists(USER_LANGS_FILE):
        return {}
    try:
        with open(USER_LANGS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_language(user_id, lang_code):
    data = load_user_languages()
    data[str(user_id)] = lang_code
    with open(USER_LANGS_FILE, 'w') as f:
        json.dump(data, f)

def get_user_lang(user_id, user_obj_lang=None):
    """
    1. Ищем в сохраненных
    2. Если нет, берем язык системы Telegram
    3. Иначе английский
    """
    data = load_user_languages()
    if str(user_id) in data:
        return data[str(user_id)]
    
    if user_obj_lang:
        if 'ru' in user_obj_lang: return 'ru'
        if 'uk' in user_obj_lang or 'ua' in user_obj_lang: return 'uk'
    
    return 'en'