/**
 * Telegram Bot Update Handler
 */

import { PriceService } from '../services/price.js';
import { DatabaseService } from '../services/database.js';
import { getLanguage, t } from './i18n.js';
import { 
  sendTelegramMessage, 
  editTelegramMessage, 
  deleteTelegramMessage,
  answerCallbackQuery,
  sendTelegramPhoto
} from '../utils/telegram.js';
import { formatPrice, formatLargeNumber } from '../utils/formatters.js';
import { generateChartUrl } from '../utils/chart.js';

export async function handleTelegramUpdate(update, env) {
  const db = new DatabaseService(env.DB);
  
  if (update.message) {
    await handleMessage(update.message, env, db);
  } else if (update.callback_query) {
    await handleCallbackQuery(update.callback_query, env, db);
  }
}

async function handleMessage(message, env, db) {
  const chatId = message.chat.id;
  const userId = message.from.id;
  const text = message.text || '';
  const isGroup = message.chat.type !== 'private';
  const lang = getLanguage(message.from.language_code);

  console.log('Processing message:', text, 'from user:', userId, 'lang:', lang);

  // Save user to database
  await db.saveUser(userId, message.from.username, message.from.first_name, lang);

  // Handle commands
  if (text.startsWith('/start')) {
    console.log('Handling /start command');
    await handleStart(chatId, userId, lang, env);
  } else if (text.startsWith('/help')) {
    console.log('Handling /help command');
    await handleHelp(chatId, lang, env);
  } else if (text.startsWith('/top10')) {
    await handleTop10(chatId, lang, env, db);
  } else if (text.startsWith('/stats') && userId.toString() === env.ADMIN_CHAT_ID) {
    await handleStats(chatId, env, db);
  } else if (text.startsWith('/broadcast') && userId.toString() === env.ADMIN_CHAT_ID) {
    await handleBroadcast(message, env, db);
  } else if (text.startsWith('/support')) {
    await handleSupport(chatId, lang, env);
  } else if (text.startsWith('/reply') && userId.toString() === env.ADMIN_CHAT_ID) {
    await handleReply(message, env);
  } else if (text.startsWith('/p ') && isGroup) {
    const coin = text.substring(3).trim();
    await handlePriceRequest(chatId, coin, lang, env, db);
  } else if (!isGroup && !text.startsWith('/')) {
    // Direct price request in private chat
    await handlePriceRequest(chatId, text.trim(), lang, env, db);
  }
}

async function handleStart(chatId, userId, lang, env) {
  const welcomeMessage = t(lang, 'welcome');
  await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, welcomeMessage, {
    reply_markup: {
      inline_keyboard: [
        [{ text: t(lang, 'btn_help'), callback_data: 'help' }],
        [{ text: t(lang, 'btn_top10'), callback_data: 'top10' }]
      ]
    }
  });
}

async function handleHelp(chatId, lang, env) {
  const helpMessage = t(lang, 'help');
  await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, helpMessage);
}

async function handleTop10(chatId, lang, env, db) {
  const waitMsg = await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, t(lang, 'loading'));
  
  try {
    const priceService = new PriceService(env);
    const topCoins = await priceService.getTop10();
    
    let message = `🏆 <b>${t(lang, 'top10_title')}</b>\n\n`;
    
    topCoins.forEach((coin, index) => {
      const trend = coin.change24h >= 0 ? '🟢' : '🔴';
      const changeStr = coin.change24h >= 0 ? '+' : '';
      message += `${index + 1}. <b>${coin.symbol.toUpperCase()}</b> - $${formatPrice(coin.price)} ${trend} ${changeStr}${coin.change24h.toFixed(2)}%\n`;
    });

    await editTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, waitMsg.result.message_id, message);
    
    // Log search
    await db.logSearch(chatId, 'TOP10');
  } catch (error) {
    console.error('Top10 error:', error);
    await editTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, waitMsg.result.message_id, t(lang, 'error'));
  }
}

async function handlePriceRequest(chatId, coin, lang, env, db) {
  if (!coin) return;

  const waitMsg = await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, t(lang, 'loading'));
  
  try {
    const priceService = new PriceService(env);
    const data = await priceService.getPrice(coin);
    
    if (!data) {
      await editTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, waitMsg.result.message_id, t(lang, 'coin_not_found'));
      return;
    }

    const trend = data.change24h >= 0 ? '🟢 ↑' : '🔴 ↓';
    const changeStr = data.change24h >= 0 ? '+' : '';
    
    let caption = `<b>${data.name} (${data.symbol.toUpperCase()})</b>\n\n`;
    caption += `💵 ${t(lang, 'price')}: $${formatPrice(data.price)}\n`;
    caption += `${trend} 24h: ${changeStr}${data.change24h.toFixed(2)}%\n\n`;
    caption += `🇺🇸 USD: $${formatPrice(data.price)}\n`;
    caption += `🇪🇺 EUR: €${formatPrice(data.price * 0.92)}\n`;
    caption += `🇺🇦 UAH: ₴${formatPrice(data.price * 41.5)}\n`;
    caption += `🇷🇺 RUB: ₽${formatPrice(data.price * 92)}\n\n`;
    caption += `📊 ${t(lang, 'market_cap')}: $${formatLargeNumber(data.marketCap)}\n`;
    caption += `📈 ${t(lang, 'volume_24h')}: $${formatLargeNumber(data.volume24h)}\n`;
    caption += `🔄 ${t(lang, 'supply')}: ${formatLargeNumber(data.circulatingSupply)} ${data.symbol.toUpperCase()}`;

    // Generate chart
    const chartUrl = generateChartUrl(data.symbol.toUpperCase(), data.change24h);
    
    // Delete loading message
    await deleteTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, waitMsg.result.message_id);
    
    // Send photo with chart
    await sendTelegramPhoto(env.TELEGRAM_BOT_TOKEN, chatId, chartUrl, caption);
    
    // Log search
    await db.logSearch(chatId, data.symbol.toUpperCase());
  } catch (error) {
    console.error('Price request error:', error);
    await editTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, waitMsg.result.message_id, t(lang, 'error'));
  }
}

async function handleStats(chatId, env, db) {
  const stats = await db.getStats();
  
  let message = `📊 <b>Bot Statistics</b>\n\n`;
  message += `👥 Total Users: ${stats.totalUsers}\n`;
  message += `🆕 New Users (24h): ${stats.newUsers}\n`;
  message += `⚡️ Active Users (24h): ${stats.activeUsers}\n`;
  message += `🔍 Total Searches: ${stats.totalSearches}\n\n`;
  
  if (stats.topCoins && stats.topCoins.length > 0) {
    message += `🏆 <b>Top 10 Searched Coins:</b>\n`;
    stats.topCoins.forEach((coin, i) => {
      message += `${i + 1}. ${coin.symbol} - ${coin.count} searches\n`;
    });
  }

  await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, message);
}

async function handleBroadcast(message, env, db) {
  const text = message.text.replace('/broadcast', '').trim();
  if (!text) {
    await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, message.chat.id, 'Usage: /broadcast <message>');
    return;
  }

  const users = await db.getAllUsers();
  let sent = 0;
  
  for (const user of users) {
    try {
      await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, user.user_id, text);
      sent++;
      await sleep(50);
    } catch (error) {
      console.error(`Failed to send to ${user.user_id}:`, error);
    }
  }

  await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, message.chat.id, `Broadcast sent to ${sent}/${users.length} users`);
}

async function handleSupport(chatId, lang, env) {
  const supportMessage = t(lang, 'support_info');
  await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, supportMessage);
}

async function handleReply(message, env) {
  const parts = message.text.split(' ');
  if (parts.length < 3) {
    await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, message.chat.id, 'Usage: /reply <user_id> <message>');
    return;
  }

  const userId = parts[1];
  const replyText = parts.slice(2).join(' ');
  
  try {
    await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, userId, `📬 <b>Support Reply:</b>\n\n${replyText}`);
    await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, message.chat.id, '✅ Reply sent successfully');
  } catch (error) {
    await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, message.chat.id, '❌ Failed to send reply');
  }
}

async function handleCallbackQuery(query, env, db) {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;
  const lang = getLanguage(query.from.language_code);

  if (data === 'help') {
    await handleHelp(chatId, lang, env);
  } else if (data === 'top10') {
    await handleTop10(chatId, lang, env, db);
  }

  await answerCallbackQuery(env.TELEGRAM_BOT_TOKEN, query.id);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}