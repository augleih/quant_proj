import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from config.settings import ACTIVE_TICKERS, PRICES_HISTORY_DAYS
from config.logging import logger
from database.db_manager import save_prices

def fetch_prices() -> pd.DataFrame:
    end = datetime.now()
    start = end - timedelta(days=PRICES_HISTORY_DAYS)

    logger.info(f"[PriceFetcher] Fetching {len(ACTIVE_TICKERS)} tickers from {start.date()} to {end.date()}")

    df = yf.download(
        tickers = ACTIVE_TICKERS,
        start = start.strftime("%Y-%m-%d"),
        end = end.strftime("%Y-%m-%d"),
        interval = "1d",
        auto_adjust = True,
        progress = False
    )

    records = []
    for ticker in ACTIVE_TICKERS:
        try:
            ticker_df = (
                df.xs(ticker, level="Ticker", axis=1)
                if isinstance(df.columns, pd.MultiIndex)
                else df
            )
            for date, row in ticker_df.iterrows():
                records.append({
                    "date": date,
                    "ticker": ticker,
                    "open": row.get("Open"),
                    "high": row.get("High"),
                    "low": row.get("Low"),
                    "close": row.get("Close"),
                    "volume": row.get("Volume"),
                })
        except KeyError:
            continue

    ohlcv_df = pd.DataFrame(records).dropna(subset=["close"])
    save_prices(ohlcv_df)
    logger.info(f"[PriceFetcher] Saved {len(ohlcv_df)} OHLCV rows to DB")
    return ohlcv_df

if __name__ == "__main__":
    fetch_prices()