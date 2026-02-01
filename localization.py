# localization.py

TEXTS = {
    'en': {
        'start': "👋 Hi! I'm CoinLuma.\nSend me a cryptocurrency ticker (e.g., BTC, ETH, TON) to get the current price and a 24h chart.",
        'help': "Commands:\n/start - Restart bot\n/info - About bot\n/support - Contact admin\n\nJust send a ticker (e.g. BTC) to get price.",
        'info': "CoinLuma Bot v2.2\nData sources: CoinGecko, CoinCap, CryptoCompare.\nCreated by @al3xg0r",
        'support_prompt': "Write your message for the admin:",
        'support_sent': "Message sent!",
        'support_cancel': "Cancelled.",
        'error_fetch': "⚠️ Error fetching data. Try again later.",
        'not_found': "🔍 Coin not found.",
        'price_msg': "💰 **{name} ({symbol})**\n💵 USD: `{usd}`\n💶 EUR: `{eur}`\n🇺🇦 UAH: `{uah}`\nrub RUB: `{rub}`",
        'change_24h': "Change 24h"
    },
    'ru': {
        'start': "👋 Привет! Я CoinLuma.\nОтправь мне тикер криптовалюты (например, BTC, ETH, TON), чтобы получить курс и график за 24 часа.",
        'help': "Команды:\n/start - Перезапуск\n/info - Информация\n/support - Написать админу\n\nПросто отправь тикер (например BTC).",
        'info': "CoinLuma Bot v2.2\nИсточники: CoinGecko, CoinCap, CryptoCompare.\nРазработчик: @al3xg0r",
        'support_prompt': "Напишите сообщение для администратора:",
        'support_sent': "Сообщение отправлено!",
        'support_cancel': "Отменено.",
        'error_fetch': "⚠️ Ошибка получения данных.",
        'not_found': "🔍 Монета не найдена.",
        'price_msg': "💰 **{name} ({symbol})**\n💵 USD: `{usd}`\n💶 EUR: `{eur}`\n🇺🇦 UAH: `{uah}`\nrub RUB: `{rub}`",
        'change_24h': "Изменение 24ч"
    },
    'uk': {
        'start': "👋 Привіт! Я CoinLuma.\nНадішли мені тікер криптовалюти (наприклад, BTC, ETH, TON), щоб отримати курс та графік за 24 години.",
        'help': "Команди:\n/start - Перезапуск\n/info - Інформація\n/support - Написати адміну\n\nПросто надішли тікер (наприклад BTC).",
        'info': "CoinLuma Bot v2.2\nДжерела: CoinGecko, CoinCap, CryptoCompare.\nРозробник: @al3xg0r",
        'support_prompt': "Напишіть повідомлення для адміністратора:",
        'support_sent': "Повідомлення надіслано!",
        'support_cancel': "Скасовано.",
        'error_fetch': "⚠️ Помилка отримання даних.",
        'not_found': "🔍 Монету не знайдено.",
        'price_msg': "💰 **{name} ({symbol})**\n💵 USD: `{usd}`\n💶 EUR: `{eur}`\n🇺🇦 UAH: `{uah}`\nrub RUB: `{rub}`",
        'change_24h': "Зміна за 24г"
    }
}