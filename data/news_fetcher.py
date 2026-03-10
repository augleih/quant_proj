import feedparser
import requests
import pandas as pd
from datetime import datetime
from config.settings import SP500_TOP50, NEWS_API_KEY
from database.db_manager import save_news

def fetch_yahoo_rss(ticker: str) -> list[dict]:
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    results = []

    for entry in feed.entries[:5]:  # latest 5 headlines per ticker
        results.append({
            "ticker": ticker,
            "title": entry.get("title", ""),
            "source": "yahoo_rss",
            "fetched_at": datetime.utcnow().isoformat()
        })
    return results

def fetch_newsapi(ticker: str) -> list[dict]:
    if not NEWS_API_KEY:
        return []
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={ticker}&language=en&sortBy=publishedAt"
        f"&pageSize=5&apiKey={NEWS_API_KEY}"
    )
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return []
    articles = resp.json().get("articles", [])
    return [{
        "ticker": ticker,
        "title": a.get("title", ""),
        "published": a.get("publishedAt", ""),
        "source": "newsapi",
        "fetched_at": datetime.utcnow().isoformat()
    } for a in articles]

def fetch_all_news() -> pd.DataFrame:
    all_news = []
    for ticker in SP500_TOP50:
        all_news.extend(fetch_yahoo_rss(ticker))
        all_news.extend(fetch_newsapi(ticker))
        print(f"[NewsFetcher] {ticker}: {len(all_news)} total articles so far")

    df = pd.DataFrame(all_news).drop_duplicates(subset=["ticker", "title"])
    save_news(df)
    print(f"[NewsFetcher] Saved {len(df)} articles to DB")
    return df

if __name__ == "__main__":
    fetch_all_news()