# localization.py

TEXTS = {
    'en': {
        'start': "👋 Hello! I am Coinlumabot.\nI show crypto rates in USD, EUR, UAH, RUB.\nType the coin name (e.g., 'bitcoin' or 'btc').\n/help for more info.",
        'help': "ℹ️ **How to use:**\nJust send me a ticker (BTC) or name (Ethereum).\n\nCommands:\n/start - Restart\n/info - Bot info\n/support - Write to admin",
        'info': "🤖 **Coinlumabot**\nData source: CoinGecko & CoinCap.\nUpdates: Every 10 mins (cached).",
        'support_prompt': "📝 Please write your message for support (report a bug or suggest a feature):",
        'support_sent': "✅ Message sent to administrator!",
        'support_cancel': "❌ Operation cancelled.",
        'error_fetch': "⚠️ Error fetching data. Please try again later.",
        'not_found': "❌ Cryptocurrency not found. Check the name and try again.",
        'price_msg': "💰 **{name} ({symbol})**\n\n🇺🇸 USD: ${usd}\n🇪🇺 EUR: €{eur}\n🇺🇦 UAH: ₴{uah}\n🇷🇺 RUB: ₽{rub}",
        'language_set': "🇬🇧 Language set to English.",
        'admin_alert': "🚨 **Bot Error Alert**\nBot stopped working unexpectedly.\nError: {error}"
    },
    'ru': {
        'start': "👋 Привет! Я Coinlumabot.\nЯ показываю курс криптовалют в USD, EUR, UAH, RUB.\nНапиши название (например, 'bitcoin' или 'btc').\n/help для инфо.",
        'help': "ℹ️ **Как использовать:**\nПросто отправь тикер (BTC) или имя (Ethereum).\n\nКоманды:\n/start - Перезапуск\n/info - Инфо о боте\n/support - Написать админу",
        'info': "🤖 **Coinlumabot**\nИсточник: CoinGecko & CoinCap.\nОбновление: Раз в 10 минут (кэш).",
        'support_prompt': "📝 Пожалуйста, напишите ваше сообщение для поддержки (ошибка или идея):",
        'support_sent': "✅ Сообщение отправлено администратору!",
        'support_cancel': "❌ Операция отменена.",
        'error_fetch': "⚠️ Ошибка получения данных. Попробуйте позже.",
        'not_found': "❌ Криптовалюта не найдена. Проверьте название.",
        'price_msg': "💰 **{name} ({symbol})**\n\n🇺🇸 USD: ${usd}\n🇪🇺 EUR: €{eur}\n🇺🇦 UAH: ₴{uah}\n🇷🇺 RUB: ₽{rub}",
        'language_set': "🇷🇺 Язык установлен: Русский.",
        'admin_alert': "🚨 **Ошибка Бота**\nБот упал с ошибкой.\nТекст: {error}"
    },
    'uk': {
        'start': "👋 Привіт! Я Coinlumabot.\nЯ показую курс криптовалют в USD, EUR, UAH, RUB.\nНапиши назву (наприклад, 'bitcoin' або 'btc').\n/help для інфо.",
        'help': "ℹ️ **Як користуватись:**\nПросто надішли тікер (BTC) або назву (Ethereum).\n\nКоманди:\n/start - Перезапуск\n/info - Інфо про бота\n/support - Написати адміну",
        'info': "🤖 **Coinlumabot**\nДжерело: CoinGecko & CoinCap.\nОновлення: Раз на 10 хвилин (кеш).",
        'support_prompt': "📝 Будь ласка, напишіть ваше повідомлення для підтримки:",
        'support_sent': "✅ Повідомлення надіслано адміністратору!",
        'support_cancel': "❌ Операцію скасовано.",
        'error_fetch': "⚠️ Помилка отримання даних. Спробуйте пізніше.",
        'not_found': "❌ Криптовалюту не знайдено. Перевірте назву.",
        'price_msg': "💰 **{name} ({symbol})**\n\n🇺🇸 USD: ${usd}\n🇪🇺 EUR: €{eur}\n🇺🇦 UAH: ₴{uah}\n🇷🇺 RUB: ₽{rub}",
        'language_set': "🇺🇦 Мову встановлено: Українська.",
        'admin_alert': "🚨 **Помилка Бота**\nБот впав з помилкою.\nТекст: {error}"
    }
}