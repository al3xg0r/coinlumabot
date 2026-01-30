# CoinLumaBot

CoinLumaBot is a Telegram bot that instantly shows the current price of any cryptocurrency.  
Just type the name of the cryptocurrency, and the bot will reply with the latest rate.

The bot supports multiple languages and can automatically detect the user's language.  
You can also manually select the language via the convenient menu.

## Key Features
- Get real-time prices for any cryptocurrency
- Multi-language support (RU/EN/UA)
- Easy-to-use menu for quick access to functions
- Lightweight structure for easy future expansion

## Setup
Create a `.env` file in the project root with the following content:

> BOT_TOKEN=your_bot_token_from_BotFather  
ADMIN_ID=123456789
COINGECKO_API_KEY=AB-1A2B3C4D5...

- `BOT_TOKEN` — your Telegram bot token from BotFather  
- `ADMIN_ID` — your Telegram user ID (used for admin commands, notifications, etc.)
- `COINGECKO_API_KEY` - your CoinGeco Api Key (Demo API) 

[User Guide: How to sign up for CoinGecko Demo API and generate an API key?](https://support.coingecko.com/hc/en-us/articles/21880397454233-User-Guide-How-to-sign-up-for-CoinGecko-Demo-API-and-generate-an-API-key)

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
