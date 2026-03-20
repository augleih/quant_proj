import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (store in .env file)
NEWS_API_KEY          = os.getenv("NEWS_API_KEY")
REDDIT_CLIENT_ID      = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET  = os.getenv("REDDIT_CLIENT_SECRET")
KIS_APP_KEY           = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET        = os.getenv("KIS_APP_SECRET")
KIS_ACCOUNT_NO        = os.getenv("KIS_ACCOUNT_NO")       # e.g. "50123456-01"
ALPHA_VANTAGE_KEY     = os.getenv("ALPHA_VANTAGE_KEY")    # optional: fundamentals

# # Universe: Top 50 S&P 500 market caps
# SP500_TOP50 = [
#     "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B",
#     "AVGO", "JPM", "LLY", "V", "UNH", "XOM", "MA", "JNJ", "PG", "HD",
#     "COST", "ABBV", "MRK", "NFLX", "BAC", "KO", "CRM", "CVX", "WMT",
#     "PEP", "TMO", "MCD", "CSCO", "ACN", "LIN", "IBM", "GE", "DHR",
#     "ABT", "TXN", "PM", "CAT", "AMGN", "NEE", "MS", "RTX", "INTU",
#     "SPGI", "BLK", "ISRG", "GS", "NOW"
# ]

# --- US Semiconductors (primary) ---
US_SEMICONDUCTOR_TICKERS = [
    "NVDA",   # GPU / AI — market leader
    "TSM",    # Foundry — manufactures for NVDA/AMD/Apple
    "AMD",    # GPU/CPU competitor to NVDA
    "MU",     # DRAM — US equivalent of SK Hynix
    "AVGO",   # Networking / custom AI chips
    "AMAT",   # Chip equipment
    "ASML",   # EUV lithography monopoly (NL, US-listed ADR)
]

# --- Korean Semiconductors (secondary — included when sector relevant) ---
KR_SEMICONDUCTOR_TICKERS = [
    "005930.KS",  # Samsung Electronics — DRAM + foundry
    "000660.KS",  # SK Hynix — HBM leader, NVDA's #1 HBM supplier
    "042700.KS",  # Hanmi Semiconductor — HBM packaging equipment
]

# --- Combined semiconductor universe ---
SEMICONDUCTOR_TICKERS = US_SEMICONDUCTOR_TICKERS + KR_SEMICONDUCTOR_TICKERS
ACTIVE_TICKERS = SEMICONDUCTOR_TICKERS

MARKET_CONFIG = {
    "US": {
        "exchange":      "NYSE/NASDAQ",
        "currency":      "USD",
        "market_open":   "09:30",       # ET
        "market_close":  "16:00",       # ET
        "timezone":      "America/New_York",
        "trading_days":  252,
        "ticker_suffix": "",
    },
    "KR": {
        "exchange":      "KRX",
        "currency":      "KRW",
        "market_open":   "09:00",       # KST
        "market_close":  "15:30",       # KST
        "timezone":      "Asia/Seoul",
        "trading_days":  248,
        "ticker_suffix": ".KS",
    },
}

def get_market(ticker: str) -> str:
    """Return 'KR' if ticker ends with .KS, else 'US'."""
    return "KR" if ticker.endswith(".KS") else "US"

def get_currency(ticker: str) -> str:
    return MARKET_CONFIG[get_market(ticker)]["currency"]

# ============================================================
# Risk & Portfolio Constants
# ============================================================
PRICES_HISTORY_DAYS = 730       # 2 years of price history
RISK_FREE_RATE      = 0.043     # US 10Y treasury yield (update periodically)
TRADING_DAYS        = 252       # US default; use 248 for KR

MAX_POSITION_PCT    = 0.20      # Max 20% of portfolio in single stock
MAX_SECTOR_PCT      = 0.60      # Max 60% in one sector
RISK_PER_TRADE      = 0.02      # Max 2% of capital risked per trade (Kelly safety)
KELLY_FRACTION      = 0.5       # Half-Kelly — industry standard


# ============================================================
# Position Sizing
# ============================================================
POSITION_SIZING = {
    "method":           "signal_scaled",   # options: fixed | signal_scaled | volatility | kelly
    "base_size_usd":    1000,              # base order size in USD
    "signal_thresholds": {
        "strong_buy":   0.8,    # signal > 0.8  → 2.0x base
        "buy":          0.6,    # signal > 0.6  → 1.5x base
        "weak_buy":     0.4,    # signal > 0.4  → 1.0x base
        "weak_sell":   -0.4,    # signal < -0.4 → -1.0x base
        "sell":        -0.6,    # signal < -0.6 → -1.5x base
        "strong_sell": -0.8,    # signal < -0.8 → -2.0x base
    },
}


# ============================================================
# Stop Loss / Risk Management
# ============================================================
STOP_LOSS = {
    "mdd_reduce":       -0.05,  # -5%  MDD → sell 30%
    "mdd_caution":      -0.08,  # -8%  MDD → sell 50%
    "mdd_exit":         -0.10,  # -10% MDD → full exit (hard stop)
    "daily_loss_limit": -0.03,  # halt trading if daily P&L < -3%
}


# ============================================================
# Fundamental Factors
# ============================================================
FUNDAMENTAL_FACTORS = [
    "debt_to_equity",       # capital structure health
    "interest_coverage",    # solvency: EBIT / interest expense
    "gross_margin",         # DRAM cycle directly visible here
    "roe",                  # profitability quality (Buffett's favorite)
    "current_ratio",        # short-term liquidity
    "capex_ratio",          # forward investment signal (semis: critical)
]

FUNDAMENTAL_REFRESH_DAYS = 90   # re-fetch every quarter (earnings cycle)


# ============================================================
# News & Sentiment
# ============================================================
SENTIMENT_CONFIG = {
    "US": {
        "sources":        ["reuters", "bloomberg", "cnbc", "seekingalpha"],
        "language":       "en",
        "lookback_hours": 24,
    },
    "KR": {
        "sources":        ["koreaherald", "chosun", "edaily", "dart"],
        "language":       "ko",
        "lookback_hours": 24,
    },
}

SENTIMENT_WEIGHTS = {
    "title":   0.3,
    "summary": 0.7,    # summary carries more signal (as per your improvement)
}


# ============================================================
# Cross-Market Signal (KR close → US open lag)
# ============================================================
CROSS_MARKET = {
    "enabled": True,
    "kr_us_pairs": {
        "005930.KS": ["MU"],          # Samsung ↔ Micron (DRAM peers)
        "000660.KS": ["NVDA", "MU"],  # SK Hynix ↔ NVDA (HBM supplier), MU
    },
    "lag_hours":     14,    # approximate KR close → US open gap
    "signal_weight": 0.15,  # 15% weight in combined signal
}


# ============================================================
# KIS API (Korea Investment & Securities)
# ============================================================
KIS_CONFIG = {
    "base_url_real":  "https://openapi.koreainvestment.com:9443",
    "base_url_mock":  "https://openapivts.koreainvestment.com:29443",
    "is_mock":        True,     # IMPORTANT: set False for real trading
    "us_market_code": "NASD",   # NASD | NYSE | AMEX
    "kr_market_code": "KRX",
}


# ============================================================
# Database
# ============================================================
DB_PATH = "db/quant.db"


# ============================================================
# Logging
# ============================================================
LOG_LEVEL = "INFO"   # DEBUG | INFO | WARNING | ERROR
LOG_DIR   = "logs/"