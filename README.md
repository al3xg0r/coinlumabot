# 🪙 CoinLuma Bot

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Version-2.5.1-orange.svg)

**CoinLuma** is an advanced Telegram bot for tracking cryptocurrency prices in real-time. It features multi-source data aggregation, professional 24h charts, market insights, and a powerful administrator panel.

---

## 🚀 Key Features

### 👤 For Users
* **Multi-Source Reliability:** Aggregates prices from **CoinGecko**, **CoinMarketCap**, **CoinCap**, and **CryptoCompare**. If one API fails, the bot automatically switches to the next one.
* **24h Market Charts:** Generates beautiful, dark-themed price charts using Matplotlib.
* **Group Support:** Works in groups via the `/p` command to prevent spam.
* **Market Leaders:** The `/top10` command displays the current market leaders with trends.
* **Smart UI:** Visual trend indicators (🟢 ↑ / 🔴 ↓), currency flags (🇺🇸, 🇪🇺, 🇺🇦, 🇷🇺), and clean formatting.
* **Multilingual:** Full support for **English** 🇺🇸, **Russian** 🇷🇺, and **Ukrainian** 🇺🇦 (auto-detected).

### 🛠 For Administrators
* **Database Integration:** SQLite database to track users and search history.
* **Analytics:** `/stats` command shows total users, new users (24h), active users, and top searched coins.
* **Support System:** Users can send tickets via `/support`. Admins can reply directly from the bot using `/reply`.
* **Broadcasting:** Send mass notifications to all users using `/broadcast`.
* **Daily Reports:** Automatic statistical report sent to the admin every day at 10:00 (Kyiv time).

---

## ⚙️ Installation & Setup

### Clone the repository
```bash
git clone https://github.com/al3xg0r/coinlumabot.git
cd coinlumabot
```

### Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate   # Windows
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configuration (.env)
Create a `.env` file in the root directory. You will need to obtain API keys from the providers below.

**Where to get API keys:**
* **Telegram Bot Token:** Get it from [@BotFather](https://t.me/BotFather).
* **CoinGecko:** Get a Demo Key [here](https://www.coingecko.com/en/api/pricing).
* **CoinMarketCap:** Sign up for a free Basic plan [here](https://pro.coinmarketcap.com/login).

**Paste this into your `.env` file:**

```env
# Required
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_numeric_id

# API Keys (Highly Recommended for stability)
COINGECKO_API_KEY=your_coingecko_key
COINMARKETCAP_API_KEY=your_coinmarketcap_key
```

### Run the bot
```bash
python app.py
```

---

## 👥 Adding to Groups

To use CoinLuma in Telegram Groups or Channels:

1. **Add the bot** to your group as a member (or admin).
2. To allow the bot to read commands, go to **BotFather** -> Bot Settings -> Group Privacy -> **Turn Off**.
3. Use the special group command:
   * `/p <ticker>` (e.g., `/p BTC`, `/p ETH`)
   * `/top10` (Shows market leaders)

*Note: The bot ignores regular text messages in groups to prevent spam.*

---

## 🤖 Commands

| Command | Description | Access |
| :--- | :--- | :--- |
| `/start` | Start bot & register in DB | All |
| `/help` | Show command list | All |
| `/top10` | Show Top 10 Crypto by Market Cap | All |
| `/p <ticker>` | Get price (Group mode) | All |
| `/info` | Version & Developer info | All |
| `/support` | Send a message to Admin | All |
| `BTC` | (Any text) Get price (Private Only) | All |
| `/stats` | View bot statistics | **Admin** |
| `/reply ID Text` | Reply to a specific user | **Admin** |
| `/broadcast Text` | Send message to ALL users | **Admin** |

---

## 🏗 Tech Stack

* **Language:** Python 3.11
* **Framework:** `python-telegram-bot` (v20+ Async)
* **Database:** SQLite
* **Visualization:** Matplotlib, Pandas
* **Scheduling:** APScheduler
* **Data Sources:** CoinGecko, CoinMarketCap, CoinCap, CryptoCompare

---

## 👨‍💻 Developer

Created by [@al3xg0r](https://github.com/al3xg0r)

Project is open for contributions! Feel free to open issues or pull requests.