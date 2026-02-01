# app.py
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
# Импортируем инициализацию БД
from database import init_db 
from handlers import (
    start, help_command, info_command, 
    support_start, support_receive, cancel, 
    handle_crypto_request, stats_command, SUPPORT_STATE # <-- Добавил stats_command
)

def main():
    # 1. Создаем таблицы при старте
    init_db()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation Handler (Support)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('support', support_start)],
        states={
            SUPPORT_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_receive)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    
    # 2. Регистрируем команду статистики
    app.add_handler(CommandHandler("stats", stats_command))
    
    app.add_handler(conv_handler)
    
    # Обработчик текста (должен быть последним)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_crypto_request))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()