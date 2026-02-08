# handlers.py
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes, ConversationHandler
from localization import TEXTS
from utils import get_user_lang, save_user_language, logger, ADMIN_ID
from services import CryptoService
from database import add_user, log_search, get_statistics, get_all_users

SUPPORT_STATE = 1

async def start(update, context):
    u = update.effective_user
    l = get_user_lang(u.id, u.language_code)
    save_user_language(u.id, l)
    add_user(u.id, u.username, u.first_name, l)
    await update.message.reply_text(TEXTS[l]['start'])

async def help_command(update, context):
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['help'], parse_mode='Markdown')

async def info_command(update, context):
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['info'], parse_mode='Markdown')

async def support_start(update, context):
    # Поддержка работает только в ЛС
    if update.effective_chat.type != ChatType.PRIVATE:
        return ConversationHandler.END
        
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['support_prompt'])
    return SUPPORT_STATE

async def support_receive(update, context):
    u = update.effective_user
    l = get_user_lang(u.id)
    reply_cmd = f"/reply {u.id}"
    msg = (
        f"📩 **New Support Message**\n"
        f"From: {u.first_name} (@{u.username})\n"
        f"ID: `{u.id}`\n\n"
        f"📝 Text:\n{update.message.text}\n\n"
        f"👇 Click to reply:\n`{reply_cmd}`"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode='Markdown')
    await update.message.reply_text(TEXTS[l]['support_sent'])
    return ConversationHandler.END

async def cancel(update, context):
    l = get_user_lang(update.effective_user.id)
    await update.message.reply_text(TEXTS[l]['support_cancel'])
    return ConversationHandler.END

# --- Админские функции ---
async def reply_command(update, context):
    if update.effective_user.id != ADMIN_ID: return
    try:
        if len(context.args) < 2:
            await update.message.reply_text("⚠️ Use: `/reply <user_id> <message>`", parse_mode='Markdown')
            return
        user_id = int(context.args[0])
        text = " ".join(context.args[1:])
        l = get_user_lang(user_id) 
        response_text = TEXTS[l]['admin_reply'].format(text=text)
        await context.bot.send_message(chat_id=user_id, text=response_text, parse_mode='Markdown')
        await update.message.reply_text(f"✅ Sent to `{user_id}`", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def broadcast_command(update, context):
    if update.effective_user.id != ADMIN_ID: return
    msg_text = " ".join(context.args)
    if not msg_text:
        await update.message.reply_text("⚠️ Use: `/broadcast <message>`", parse_mode='Markdown')
        return
    users = get_all_users()
    count = len(users)
    l = get_user_lang(ADMIN_ID)
    await update.message.reply_text(TEXTS[l]['broadcast_start'].format(count=count))
    success_count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=msg_text, parse_mode='Markdown')
            success_count += 1
        except Exception as e:
            logger.error(f"Broadcast fail for {uid}: {e}")
    await update.message.reply_text(f"{TEXTS[l]['broadcast_done']}\n✅ Delivered: {success_count}/{count}")

async def stats_command(update, context):
    if update.effective_user.id != ADMIN_ID: return 
    s = get_statistics()
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

# --- Топ-10 ---
async def top10_command(update, context):
    l = get_user_lang(update.effective_user.id)
    coins = CryptoService.get_top_10()
    if not coins:
        await update.message.reply_text(TEXTS[l]['top10_error'])
        return
    msg = TEXTS[l]['top10_header']
    for idx, coin in enumerate(coins):
        symbol = coin['symbol'].upper()
        price = coin['current_price']
        change = coin.get('price_change_percentage_24h', 0)
        arrow_str = "🟢 ↑" if change >= 0 else "🔴 ↓"
        msg += f"**{idx+1}. {symbol}:** `{price} $` ({arrow_str} {change:.2f}%)\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- Универсальная функция обработки (внутренняя) ---
async def _process_price_request(update, context, query):
    l = get_user_lang(update.effective_user.id)
    
    # Игнорируем длинные сообщения (защита от спама)
    if len(query) > 20: return

    log_search(update.effective_user.id, query)
    wait = await update.message.reply_text("⏳ ...")
    
    data = CryptoService.get_coin_price(query)
    if not data:
        await wait.edit_text(TEXTS[l]['not_found'])
        return

    change_val = data.get('change_24h', 0)
    if change_val >= 0:
        trend_emoji = "📈"
        arrow_str = "🟢 ↑" 
    else:
        trend_emoji = "📉"
        arrow_str = "🔴 ↓"
    
    msg = TEXTS[l]['price_msg'].format(
        name=data['name'], symbol=data['symbol'],
        usd=data['usd'], eur=data['eur'], uah=data['uah'], rub=data['rub']
    )
    msg += f"\n\n{trend_emoji} {TEXTS[l]['change_24h']}: {arrow_str} {change_val:.2f}%"

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

# --- Обработчик текста (Только ЛС) ---
async def handle_crypto_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если это ГРУППА или КАНАЛ - игнорируем обычный текст
    if update.effective_chat.type != ChatType.PRIVATE:
        return
    
    q = update.message.text
    if not q: return
    await _process_price_request(update, context, q)

# --- Обработчик команды /p или /price (Для групп) ---
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        # Можно вывести подсказку, как пользоваться
        return
    
    q = context.args[0]
    await _process_price_request(update, context, q)