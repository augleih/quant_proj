import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from config.settings import SP500_TOP50, PRICES_HISTORY_DAYS
from database.db_manager import save_prices

def fetch_prices() -> pd.DataFrame:
    end = datetime.now()
    start = end - timedelta(days=PRICES_HISTORY_DAYS)

    print(f"[PriceFetcher] Fetching {len(SP500_TOP50)} tickers from {start.date()} to {end.date()}")

    df = yf.download(
        tickers = SP500_TOP50,
        start = start.strftime("%Y-%m-%d"),
        end = end.strftime("%Y-%m-%d"),
        interval = "1d",
        auto_adjust = True,
        progress = False
    )

    # Keep only Close prices for now
    close_df = df["Close"]
    close_df.dropna(how="all", inplace=True)

    save_prices(close_df)
    print(f"[PricesFetcher] Saved {close_df.shape} prices data to DB")
    return close_df

if __name__ == "__main__":
    fetch_prices()