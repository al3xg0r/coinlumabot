# handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from localization import TEXTS
from utils import get_user_lang, save_user_language, logger, ADMIN_ID
from services import CryptoService

# Состояния для разговора Support
SUPPORT_STATE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Определяем и сохраняем язык при первом старте
    lang = get_user_lang(user.id, user.language_code)
    save_user_language(user.id, lang)
    
    await update.message.reply_text(TEXTS[lang]['start'])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    await update.message.reply_text(TEXTS[lang]['help'], parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    await update.message.reply_text(TEXTS[lang]['info'], parse_mode='Markdown')

# --- Логика Support ---
async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    await update.message.reply_text(TEXTS[lang]['support_prompt'])
    return SUPPORT_STATE

async def support_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_lang(user.id)
    text = update.message.text
    
    # Отправка админу
    admin_msg = f"📩 **Support Message**\nFrom: {user.first_name} (@{user.username})\nID: {user.id}\n\nMessage:\n{text}"
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        await update.message.reply_text(TEXTS[lang]['support_sent'])
    except Exception as e:
        logger.error(f"Failed to send support msg: {e}")
        await update.message.reply_text(TEXTS[lang]['error_fetch'])
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    await update.message.reply_text(TEXTS[lang]['support_cancel'])
    return ConversationHandler.END

# --- Обработка криптовалют ---
async def handle_crypto_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    query = update.message.text
    
    if len(query) > 20: 
        return

    # 1. Отправляем "Ожидайте..."
    wait_msg = await update.message.reply_text("⏳ ...")
    
    # 2. Получаем данные
    data = CryptoService.get_coin_price(query)
    
    # 3. Обработка результата
    if data == "error":
        await wait_msg.edit_text(TEXTS[lang]['error_fetch'])
    
    elif data is None:
        await wait_msg.edit_text(TEXTS[lang]['not_found'])
    
    else:
        # Формируем текст (убрали 💰, так как будет картинка)
        msg = TEXTS[lang]['price_msg'].format(
            name=data['name'],
            symbol=data['symbol'],
            usd=data['usd'],
            eur=data['eur'],
            uah=data['uah'],
            rub=data['rub']
        )

        # Удаляем сообщение "Ожидайте..."
        await wait_msg.delete()

        # Если есть картинка — шлем фото с подписью
        if data.get('image'):
            try:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=data['image'],
                    caption=msg,
                    parse_mode='Markdown'
                )
            except Exception:
                # Если ссылка на картинку битая, шлем просто текст
                await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            # Если картинки нет (например, из CoinCap)
            await update.message.reply_text(msg, parse_mode='Markdown')