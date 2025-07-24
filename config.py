# config.py

# Trading parameters
TRADE_AMOUNT = 1000.0  # Starting FDUSD amount
BASE_CURRENCY = "FDUSD"
INTERMEDIATE_CURRENCY = "BTC"
THIRD_CURRENCY = "USDT"
MIN_PROFIT_THRESHOLD = 0.1  # Minimum profit threshold in percentage

# API credentials
API_KEY = ""
API_SECRET = ""

# Safety features
DRY_RUN = True  # Set to False to execute real trades
MAX_LOSS_PROTECTION = 0.5  # Maximum loss in percentage
RATE_LIMITING_DELAY = 2  # Delay in seconds between each check

# Trading fees
MAKER_FEE = 0.001  # 0.1%
TAKER_FEE = 0.001  # 0.1%

# Telegram
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
