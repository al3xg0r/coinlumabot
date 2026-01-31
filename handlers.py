# handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from localization import TEXTS
from utils import get_user_lang, save_user_language, logger, ADMIN_ID
from services import CryptoService

SUPPORT_STATE = 1

# (Остальные функции: start, help, info, support - оставляем без изменений)
async def start(update, context):
    u = update.effective_user
    l = get_user_lang(u.id, u.language_code)
    save_user_language(u.id, l)
    await update.message.reply_text(TEXTS[l]['start'])

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

# --- Главное изменение здесь ---
async def handle_crypto_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = get_user_lang(update.effective_user.id)
    q = update.message.text
    if not q or len(q) > 30: return

    wait = await update.message.reply_text("⏳ ...")
    
    # 1. Получаем цену
    data = CryptoService.get_coin_price(q)
    
    if not data:
        await wait.edit_text(TEXTS[l]['not_found'])
        return

    # 2. Формируем текст
    change_emoji = "🟢" if data.get('change_24h', 0) >= 0 else "🔴"
    msg = TEXTS[l]['price_msg'].format(
        name=data['name'], symbol=data['symbol'],
        usd=data['usd'], eur=data['eur'], uah=data['uah'], rub=data['rub']
    )
    msg += f"\nChange 24h: {change_emoji} {data.get('change_24h', 0):.2f}%"

    await wait.delete()

    # 3. Пробуем получить график (если есть ID монеты)
    chart_file = None
    if data.get('id'):
        chart_file = CryptoService.get_chart(data['id'])

    # 4. Отправка ответа
    try:
        if chart_file:
            # Шлем с графиком
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, 
                photo=chart_file, 
                caption=msg, 
                parse_mode='Markdown'
            )
        elif data.get('image'):
            # Шлем с логотипом (если график не удалось сделать)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, 
                photo=data['image'], 
                caption=msg, 
                parse_mode='Markdown'
            )
        else:
            # Шлем только текст
            await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Send error: {e}")
        await update.message.reply_text(msg, parse_mode='Markdown')