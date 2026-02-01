# app.py
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from config import BOT_TOKEN, ADMIN_ID
from database import init_db, get_statistics 
from handlers import (
    start, help_command, info_command, 
    support_start, support_receive, cancel, 
    handle_crypto_request, stats_command, SUPPORT_STATE
)

# Функция отчета
async def send_daily_stats(app):
    s = get_statistics()
    top_list = "\n".join([f"{i+1}. {c[0]} — {c[1]}" for i, c in enumerate(s['top_coins'])])
    
    msg = (
        f"📅 **Ежедневный отчет (10:00)**\n\n"
        f"👥 Всего пользователей: `{s['total_users']}`\n"
        f"🆕 Новых (24ч): `{s['new_24h']}`\n"
        f"🔥 Активных (24ч): `{s['active_24h']}`\n"
        f"🔍 Запросов всего: `{s['total_requests']}`\n\n"
        f"🏆 **Топ монет:**\n{top_list}"
    )
    # Используем bot напрямую из созданного приложения
    await app.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode='Markdown')

def main():
    init_db()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Kyiv"))
    # Передаем app через args (кортеж, поэтому запятая в конце обязательна)
    scheduler.add_job(send_daily_stats, 'cron', hour=10, minute=0, args=(app,))
    scheduler.start()

    # Обработчики
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('support', support_start)],
        states={SUPPORT_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_receive)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_crypto_request))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()