# handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from localization import TEXTS
from utils import get_user_lang, save_user_language, logger, ADMIN_ID
from services import CryptoService
# Импортируем БД
from database import add_user, log_search, get_statistics

SUPPORT_STATE = 1

# --- Админская команда ---
async def stats_command(update, context):
    user_id = update.effective_user.id
    # Проверка на админа
    if user_id != ADMIN_ID:
        return # Просто игнорируем чужаков

    s = get_statistics()
    
    # Красивое формирование топа монет
    top_list = "\n".join([f"{i+1}. {c[0]} — {c[1]}" for i, c in enumerate(s['top_coins'])])
    
    msg = (
        f"📊 **Bot Statistics**\n\n"
        f"👥 Users Total: `{s['total_users']}`\n"
        f"🆕 New (24h): `{s['new_24h']}`\n"
        f"🔥 Active (24h): `{s['active_24h']}`\n"
        f"🔍 Total Requests: `{s['total_requests']}`\n\n"
        f"🏆 **Top Coins:**\n{top_list}"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- Обновленный Start ---
async def start(update, context):
    u = update.effective_user
    l = get_user_lang(u.id, u.language_code)
    save_user_language(u.id, l)
    
    # --> Запись в БД
    add_user(u.id, u.username, u.first_name, l)
    
    await update.message.reply_text(TEXTS[l]['start'])

# --- Обновленный Crypto Request ---
async def handle_crypto_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    l = get_user_lang(u.id)
    q = update.message.text
    if not q or len(q) > 30: return

    # --> Логируем запрос в БД
    log_search(u.id, q)
    
    # ... (Весь остальной код без изменений: wait message, get price, chart, send) ...
    wait = await update.message.reply_text("⏳ ...")
    
    data = CryptoService.get_coin_price(q)
    
    if not data:
        await wait.edit_text(TEXTS[l]['not_found'])
        return

    change_val = data.get('change_24h', 0)
    trend_emoji = "📈" if change_val >= 0 else "📉"
    arrow_emoji = "⬆️" if change_val >= 0 else "⬇️"
    
    msg = TEXTS[l]['price_msg'].format(
        name=data['name'], symbol=data['symbol'],
        usd=data['usd'], eur=data['eur'], uah=data['uah'], rub=data['rub']
    )
    msg += f"\n\n{trend_emoji} {TEXTS[l]['change_24h']}: {arrow_emoji} {change_val:.2f}%"

    await wait.delete()

    chart_file = None
    if data.get('id'):
        chart_file = CryptoService.get_chart(data['id'])

    try:
        if chart_file:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart_file, caption=msg, parse_mode='Markdown')
        elif data.get('image'):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=data['image'], caption=msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Send error: {e}")
        await update.message.reply_text(msg, parse_mode='Markdown')

# Остальные функции (help, info, support...) без изменений
async def help_command(update, context):
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['help'], parse_mode='Markdown')

async def info_command(update, context):
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['info'], parse_mode='Markdown')

async def support_start(update, context):
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['support_prompt'])
    return SUPPORT_STATE

async def support_receive(update, context):
    u = update.effective_user
    l = get_user_lang(u.id)
    msg = f"📩 **Support**\nFrom: {u.first_name} (@{u.username})\nID: {u.id}\n\n{update.message.text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text(TEXTS[l]['support_sent'])
    return ConversationHandler.END

async def cancel(update, context):
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['support_cancel'])
    return ConversationHandler.END