# database.py
import sqlite3
import os
from datetime import datetime, timedelta

# Получаем абсолютный путь к папке бота
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "bot.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY,
                 username TEXT,
                 first_name TEXT,
                 joined_date TIMESTAMP,
                 language TEXT
                 )''')
    # Таблица запросов (логов)
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 ticker TEXT,
                 search_date TIMESTAMP
                 )''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, language):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Добавляем, если нет. Если есть - обновляем язык
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date, language) VALUES (?, ?, ?, ?, ?)",
              (user_id, username, first_name, datetime.now(), language))
    c.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
    conn.commit()
    conn.close()

def log_search(user_id, ticker):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO requests (user_id, ticker, search_date) VALUES (?, ?, ?)",
              (user_id, ticker.upper(), datetime.now()))
    conn.commit()
    conn.close()

def get_statistics():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Всего пользователей
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    # 2. Новых за 24ч
    day_ago = datetime.now() - timedelta(days=1)
    c.execute("SELECT COUNT(*) FROM users WHERE joined_date > ?", (day_ago,))
    new_users_24h = c.fetchone()[0]

    # 3. Активных за 24ч (кто делал запросы)
    c.execute("SELECT COUNT(DISTINCT user_id) FROM requests WHERE search_date > ?", (day_ago,))
    active_24h = c.fetchone()[0]

    # 4. Всего запросов
    c.execute("SELECT COUNT(*) FROM requests")
    total_requests = c.fetchone()[0]

    # 5. Топ 5 монет
    c.execute("SELECT ticker, COUNT(*) as cnt FROM requests GROUP BY ticker ORDER BY cnt DESC LIMIT 5")
    top_coins = c.fetchall() 

    conn.close()
    
    return {
        'total_users': total_users,
        'new_24h': new_users_24h,
        'active_24h': active_24h,
        'total_requests': total_requests,
        'top_coins': top_coins
    }

def get_all_users():
    """Возвращает список ID всех пользователей для рассылки"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users