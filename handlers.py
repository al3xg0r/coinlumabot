# handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from localization import TEXTS
from utils import get_user_lang, save_user_language, logger, ADMIN_ID
from services import CryptoService

SUPPORT_STATE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_lang(user.id, user.language_code)
    save_user_language(user.id, lang)
    await update.message.reply_text(TEXTS[lang]['start'])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[lang]['help'], parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[lang]['info'], parse_mode='Markdown')

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[lang]['support_prompt'])
    return SUPPORT_STATE

async def support_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_lang(user.id)
    admin_msg = f"📩 **Support**\nFrom: {user.first_name} (@{user.username})\nID: {user.id}\n\n{update.message.text}"
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        await update.message.reply_text(TEXTS[lang]['support_sent'])
    except:
        await update.message.reply_text(TEXTS[lang]['error_fetch'])
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[lang]['support_cancel'])
    return ConversationHandler.END

async def handle_crypto_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    query = update.message.text
    
    if not query or len(query) > 30: return

    wait_msg = await update.message.reply_text("⏳ ...")
    data = CryptoService.get_coin_price(query)
    
    try:
        if data == "error":
            await wait_msg.edit_text(TEXTS[lang]['error_fetch'])
        elif data is None:
            await wait_msg.edit_text(TEXTS[lang]['not_found'])
        else:
            msg = TEXTS[lang]['price_msg'].format(
                name=data['name'], symbol=data['symbol'],
                usd=data['usd'], eur=data['eur'], uah=data['uah'], rub=data['rub']
            )
            await wait_msg.delete()
            if data.get('image'):
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=data['image'], caption=msg, parse_mode='Markdown')
            else:
                await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Handler error: {e}")
        await update.message.reply_text(TEXTS[lang]['error_fetch'])