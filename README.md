# 🪙 CoinLuma Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-orange)](https://workers.cloudflare.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue)](https://t.me/CoinLumaBot)

A reliable, multi-source cryptocurrency price tracker bot for Telegram, powered by Cloudflare Workers.

## ✨ Features

### 🔄 Multi-Source Price Aggregation
- Aggregates data from **CoinGecko**, **CoinMarketCap**, **CoinCap**, and **CryptoCompare**
- Automatic fallback between sources for maximum reliability
- Intelligent search matching for both symbols and names

### 📊 Rich Price Information
- Real-time cryptocurrency prices
- 24-hour price charts (via QuickChart)
- Price change indicators with trend visualization
- Multi-currency conversion (USD, EUR, UAH, RUB)
- Market cap, volume, and circulating supply data

### 🌍 Multilingual Support
- Full support for **English** 🇺🇸, **Russian** 🇷🇺, and **Ukrainian** 🇺🇦
- Automatic language detection based on user preferences

### 💬 Group & Private Chat Support
- Works in private chats with direct coin queries
- Group chat support via `/p <coin>` command
- Top 10 cryptocurrencies ranking with `/top10`

### 📈 Admin Features
- User statistics and analytics
- Broadcast messaging to all users
- Daily automated reports
- Search history tracking

## 🚀 Quick Start

### Prerequisites
- Cloudflare account with Workers enabled
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Node.js 18+ installed
- Wrangler CLI

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/al3xg0r/coinlumabot.git
cd coinlumabot
```

2. **Install dependencies**
```bash
npm install
```

3. **Create D1 database**
```bash
npm run db:create
```
Copy the `database_id` and update it in `wrangler.toml`:
```toml
[[d1_databases]]
binding = "DB"
database_name = "coinlumabot"
database_id = "YOUR_DATABASE_ID_HERE"
```

4. **Initialize database schema**
```bash
npm run db:init
```

5. **Configure secrets**
```bash
# Telegram Bot Token
npm run secret:telegram

# CoinGecko API Key
npm run secret:coingecko

# CoinMarketCap API Key
npm run secret:coinmarketcap

# Admin Chat ID (your Telegram user ID)
npm run secret:admin
```

6. **Deploy to Cloudflare**
```bash
npm run deploy
```

7. **Set up Telegram webhook**
```bash
curl https://YOUR_WORKER_URL/setup
```

## 📖 Usage

### User Commands
- `/start` - Start the bot and see welcome message
- `/help` - Display help information
- `/top10` - Show top 10 cryptocurrencies by market cap
- `/p <coin>` - Get price in group chats (e.g., `/p BTC`)
- Send any coin name or symbol in private chat (e.g., `bitcoin`, `eth`, `ton`)

### Admin Commands
- `/stats` - View bot statistics
- `/broadcast <message>` - Send message to all users
- `/reply <user_id> <message>` - Reply to a specific user

## 🏗️ Architecture

coinlumabot/
├── src/
│   ├── index.js              # Main worker entry point
│   ├── bot/
│   │   ├── telegram.js       # Telegram update handler
│   │   └── i18n.js           # Internationalization
│   ├── services/
│   │   ├── price.js          # Multi-source price aggregator
│   │   └── database.js       # D1 database service
│   └── utils/
│       ├── telegram.js       # Telegram API helpers
│       ├── formatters.js     # Number formatting utilities
│       └── chart.js          # Chart generation
├── schema.sql                # Database schema
├── wrangler.toml            # Cloudflare Workers config
└── package.json             # Dependencies

## 🔧 Configuration

### Environment Variables (Cloudflare Secrets)
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `COINGECKO_API_KEY` - CoinGecko API key
- `COINMARKETCAP_API_KEY` - CoinMarketCap API key
- `ADMIN_CHAT_ID` - Telegram user ID for admin commands

### Database
The bot uses Cloudflare D1 (SQLite) for:
- User management and tracking
- Search history logging
- Statistics and analytics

## 🌟 Key Technologies

- **Runtime**: Cloudflare Workers (V8 isolates)
- **Database**: Cloudflare D1 (SQLite)
- **API Integration**: Multiple crypto data providers
- **Charts**: QuickChart API
- **Module System**: ES6 modules with `nodejs_compat` flag

## 📊 API Sources

1. **CoinGecko** - Primary source with comprehensive data
2. **CoinMarketCap** - Fallback with extensive listings
3. **CoinCap** - Free tier with real-time data
4. **CryptoCompare** - Additional fallback option

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Telegram Bot**: [@CoinLumaBot](https://t.me/CoinLumaBot)
- **Support**: [@agtsupbot](https://t.me/agtsupbot)
- **GitHub**: [al3xg0r/coinlumabot](https://github.com/al3xg0r/coinlumabot)

## 💰 Pricing

The bot runs on Cloudflare Workers free tier:
- 100,000 requests/day
- 10ms CPU time per request
- 5GB D1 database storage

Perfect for personal use and small communities!

## 🙏 Acknowledgments

- [Cloudflare Workers](https://workers.cloudflare.com/) for serverless infrastructure
- [QuickChart](https://quickchart.io/) for chart generation
- [CoinGecko](https://www.coingecko.com/), [CoinMarketCap](https://coinmarketcap.com/), [CoinCap](https://coincap.io/), and [CryptoCompare](https://www.cryptocompare.com/) for crypto data APIs

---

Made with ❤️ by [al3xg0r](https://github.com/al3xg0r)