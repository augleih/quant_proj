import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (store in .env file)
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')

# Universe: Top 50 S&P 500 market caps
SP500_TOP50 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B",
    "AVGO", "JPM", "LLY", "V", "UNH", "XOM", "MA", "JNJ", "PG", "HD",
    "COST", "ABBV", "MRK", "NFLX", "BAC", "KO", "CRM", "CVX", "WMT",
    "PEP", "TMO", "MCD", "CSCO", "ACN", "LIN", "IBM", "GE", "DHR",
    "ABT", "TXN", "PM", "CAT", "AMGN", "NEE", "MS", "RTX", "INTU",
    "SPGI", "BLK", "ISRG", "GS", "NOW"
]

# Database
DB_PATH = "db/quant.db"

# Data settings
PRICES_HISTORY_DAYS = 365