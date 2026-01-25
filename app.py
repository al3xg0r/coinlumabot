# app.py
import traceback
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN, ADMIN_ID
from handlers import start, help_command, info_command, support_start, support_receive, cancel, handle_crypto_request, SUPPORT_STATE
from utils import logger
from localization import TEXTS
import requests

def notify_admin_error(error_text):
    """Синхронная отправка ошибки админу (так как цикл событий может умереть)"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_ID,
            "text": f"🚨 **CRITICAL ERROR**\n{error_text[:4000]}" # Обрезаем если слишком длинно
        }
        requests.post(url, data=data)
    except:
        pass

def main():
    try:
        logger.info("Starting Coinlumabot...")
        
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        # Support Conversation Handler
        support_handler = ConversationHandler(
            entry_points=[CommandHandler('support', support_start)],
            states={
                SUPPORT_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_receive)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        # Регистрация хендлеров
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("info", info_command))
        application.add_handler(support_handler)
        
        # Хендлер для текстовых сообщений (тикеры)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_crypto_request))

        application.run_polling()
        
    except Exception:
        error_msg = traceback.format_exc()
        logger.critical(f"Bot crashed: {error_msg}")
        notify_admin_error(error_msg)

if __name__ == '__main__':
    main()