/**
 * CoinLuma Telegram Bot on Cloudflare Workers
 * Main entry point
 */

import { handleTelegramUpdate } from './bot/telegram.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Webhook endpoint for Telegram
    if (url.pathname === '/webhook' && request.method === 'POST') {
      try {
        const update = await request.json();
        console.log('Received update:', JSON.stringify(update));
        await handleTelegramUpdate(update, env);
        return new Response('OK', { status: 200 });
      } catch (error) {
        console.error('Error processing update:', error);
        return new Response('Error: ' + error.message, { status: 500 });
      }
    }

    // Health check endpoint
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({
        status: 'ok',
        timestamp: new Date().toISOString(),
        secrets: {
          bot_token: env.TELEGRAM_BOT_TOKEN ? 'set' : 'missing',
          coingecko: env.COINGECKO_API_KEY ? 'set' : 'missing',
          coinmarketcap: env.COINMARKETCAP_API_KEY ? 'set' : 'missing',
          admin_id: env.ADMIN_CHAT_ID ? 'set' : 'missing'
        }
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Setup webhook endpoint
    if (url.pathname === '/setup') {
      try {
        const webhookUrl = `https://coinlumabot.hubapps.workers.dev/webhook`;
        const telegramApiUrl = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/setWebhook`;
        
        console.log('Setting webhook to:', webhookUrl);
        
        const response = await fetch(telegramApiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: webhookUrl })
        });

        const result = await response.json();
        console.log('Webhook setup result:', result);
        
        return new Response(JSON.stringify(result, null, 2), {
          headers: { 'Content-Type': 'application/json' }
        });
      } catch (error) {
        console.error('Setup error:', error);
        return new Response('Setup error: ' + error.message, { status: 500 });
      }
    }

    return new Response('CoinLuma Bot is running', { status: 200 });
  }
};
