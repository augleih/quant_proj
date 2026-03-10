from data.price_fetcher import fetch_prices
from data.news_fetcher import fetch_all_news

if __name__ == "__main__":
    print("=== Quant Trading Pipeline ===")
    print("\n[1/2] Fetching price data...")
    fetch_prices()

    print("\n[2/2] Fetching news data...")
    fetch_all_news()

    print("\nPhase 1 complete. Data stored in db/quant.db")
