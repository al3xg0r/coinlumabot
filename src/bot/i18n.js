/**
 * Internationalization (i18n) Module
 * Supports: English, Russian, Ukrainian
 */

const translations = {
  en: {
    welcome: `👋 <b>Welcome to CoinLuma!</b>

I'm your cryptocurrency price tracker. I aggregate data from multiple sources for maximum reliability.

💡 <b>How to use:</b>
- Just send me a coin name or symbol (e.g., "BTC", "Bitcoin")
- Use /p &lt;coin&gt; in groups to get prices
- Use /top10 to see market leaders

📊 I provide:
✓ Real-time prices in USD, EUR, UAH, RUB
✓ 24-hour price charts
✓ Market cap & volume data
✓ Price change indicators`,
    
    help: `📖 <b>Help & Commands</b>

<b>Basic Commands:</b>
/start - Start the bot
/help - Show this help message
/top10 - Top 10 cryptocurrencies by market cap

<b>Price Lookup:</b>
Just send me a coin name or symbol:
- BTC, Bitcoin, ETH, Ethereum, etc.

<b>Group Usage:</b>
/p &lt;coin&gt; - Get price in group chats
Example: /p BTC

<b>Support:</b>
Need help? Contact @tg_agteam_bot`,

    top10_title: 'Top 10 Cryptocurrencies',
    loading: '⏳ Loading data...',
    error: '❌ An error occurred. Please try again later.',
    coin_not_found: '❌ Cryptocurrency not found. Please check the name and try again.',
    support_info: '📬 <b>Support</b>\n\nIf you need assistance, please contact our support bot: @tg_agteam_bot',
    
    price: 'Price',
    market_cap: 'Market Cap',
    volume_24h: '24h Volume',
    supply: 'Circulating Supply',
    
    btn_help: '📖 Help',
    btn_top10: '🏆 Top 10'
  },

  ru: {
    welcome: `👋 <b>Добро пожаловать в CoinLuma!</b>

Я - ваш трекер цен криптовалют. Я собираю данные из нескольких источников для максимальной надежности.

💡 <b>Как использовать:</b>
- Просто отправьте мне название или символ монеты (например, "BTC", "Bitcoin")
- Используйте /p &lt;монета&gt; в группах для получения цен
- Используйте /top10 для просмотра лидеров рынка

📊 Я предоставляю:
✓ Цены в реальном времени в USD, EUR, UAH, RUB
✓ Графики цен за 24 часа
✓ Данные о капитализации и объеме
✓ Индикаторы изменения цены`,
    
    help: `📖 <b>Справка и команды</b>

<b>Основные команды:</b>
/start - Запустить бота
/help - Показать это сообщение
/top10 - Топ 10 криптовалют по капитализации

<b>Поиск цены:</b>
Просто отправьте название или символ монеты:
- BTC, Bitcoin, ETH, Ethereum и т.д.

<b>Использование в группах:</b>
/p &lt;монета&gt; - Получить цену в групповых чатах
Пример: /p BTC

<b>Поддержка:</b>
Нужна помощь? Обратитесь к @tg_agteam_bot`,

    top10_title: 'Топ 10 криптовалют',
    loading: '⏳ Загрузка данных...',
    error: '❌ Произошла ошибка. Пожалуйста, попробуйте позже.',
    coin_not_found: '❌ Криптовалюта не найдена. Проверьте название и попробуйте снова.',
    support_info: '📬 <b>Поддержка</b>\n\nЕсли вам нужна помощь, обратитесь к нашему боту поддержки: @tg_agteam_bot',
    
    price: 'Цена',
    market_cap: 'Капитализация',
    volume_24h: 'Объём 24ч',
    supply: 'Циркулирующее предложение',
    
    btn_help: '📖 Справка',
    btn_top10: '🏆 Топ 10'
  },

  uk: {
    welcome: `👋 <b>Ласкаво просимо до CoinLuma!</b>

Я - ваш трекер цін криптовалют. Я збираю дані з кількох джерел для максимальної надійності.

💡 <b>Як використовувати:</b>
- Просто надішліть мені назву або символ монети (наприклад, "BTC", "Bitcoin")
- Використовуйте /p &lt;монета&gt; в групах для отримання цін
- Використовуйте /top10 для перегляду лідерів ринку

📊 Я надаю:
✓ Ціни в реальному часі в USD, EUR, UAH, RUB
✓ Графіки цін за 24 години
✓ Дані про капіталізацію та обсяг
✓ Індикатори зміни ціни`,
    
    help: `📖 <b>Довідка та команди</b>

<b>Основні команди:</b>
/start - Запустити бота
/help - Показати це повідомлення
/top10 - Топ 10 криптовалют за капіталізацією

<b>Пошук ціни:</b>
Просто надішліть назву або символ монети:
- BTC, Bitcoin, ETH, Ethereum тощо.

<b>Використання в групах:</b>
/p &lt;монета&gt; - Отримати ціну в групових чатах
Приклад: /p BTC

<b>Підтримка:</b>
Потрібна допомога? Зверніться до @tg_agteam_bot`,

    top10_title: 'Топ 10 криптовалют',
    loading: '⏳ Завантаження даних...',
    error: '❌ Сталася помилка. Будь ласка, спробуйте пізніше.',
    coin_not_found: '❌ Криптовалюту не знайдено. Перевірте назву та спробуйте знову.',
    support_info: '📬 <b>Підтримка</b>\n\nЯкщо вам потрібна допомога, зверніться до нашого бота підтримки: @tg_agteam_bot',
    
    price: 'Ціна',
    market_cap: 'Капіталізація',
    volume_24h: 'Обсяг 24г',
    supply: 'Циркулююче пропозиція',
    
    btn_help: '📖 Довідка',
    btn_top10: '🏆 Топ 10'
  }
};

export function getLanguage(langCode) {
  if (!langCode) return 'en';
  
  const lang = langCode.toLowerCase().substring(0, 2);
  
  if (lang === 'ru') return 'ru';
  if (lang === 'uk') return 'uk';
  return 'en';
}

export function t(lang, key) {
  return translations[lang]?.[key] || translations['en'][key] || key;
}