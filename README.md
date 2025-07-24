# Triangular Arbitrage Bot for Binance

This Python bot is designed to perform triangular arbitrage on the Binance spot trading platform. It identifies and exploits price discrepancies between three trading pairs to generate profit.

## Description

The bot continuously monitors the prices of three currency pairs (e.g., FDUSD → BTC → USDT → FDUSD) on Binance. When a profitable arbitrage opportunity is identified, the bot automatically executes the necessary trades to capitalize on the price difference.

## Features

- **Triangular Arbitrage:** Monitors two different arbitrage paths for maximum opportunities.
- **Real-time Price Monitoring:** Fetches real-time order book data for accurate calculations.
- **Configurable Parameters:** Easily configure trading amounts, currency pairs, and profit thresholds.
- **Safety Features:** Includes a dry-run mode for testing, balance verification, and a simple rollback mechanism.
- **Detailed Logging:** Logs all opportunities, trades, and errors for easy monitoring and debugging.

## Technology Stack

- **Python 3.9+**
- **Binance SDK for Spot Trading (`binance-sdk-spot`)**
- **`python-dotenv`** for secure handling of API credentials.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/triangular-arbitrage-bot.git
   cd triangular-arbitrage-bot
   ```

2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **API Credentials:**
   - Create a `.env` file in the root directory of the project.
   - Add your Binance API key and secret to the `.env` file, using `.env.example` as a template:
     ```
     API_KEY=your_api_key
     API_SECRET=your_api_secret
     ```

2. **Trading Parameters:**
   - Open the `config.py` file to adjust the trading parameters:
     - `TRADE_AMOUNT`: The amount of the base currency to be used in each trade.
     - `BASE_CURRENCY`: The starting and ending currency (e.g., "FDUSD").
     - `INTERMEDIATE_CURRENCY`: The first currency to trade into (e.g., "BTC").
     - `THIRD_CURRENCY`: The second currency to trade into (e.g., "USDT").
     - `MIN_PROFIT_THRESHOLD`: The minimum profit percentage required to execute a trade.
     - `DRY_RUN`: Set to `True` to test the bot without executing real trades. Set to `False` to enable live trading.

## Usage

To start the bot, run the following command in your terminal:

```bash
python main.py
```

The bot will then start monitoring the specified currency pairs for arbitrage opportunities and execute trades when the conditions are met.

## Disclaimer

Trading cryptocurrencies involves significant risk. This bot is provided for educational purposes only and should not be used for live trading without a thorough understanding of the risks involved. The author is not responsible for any financial losses incurred from the use of this bot.
