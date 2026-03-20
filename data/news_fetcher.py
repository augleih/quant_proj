import feedparser
import requests
import pandas as pd
from datetime import datetime
from config.settings import ACTIVE_TICKERS, NEWS_API_KEY
from config.logging import logger
from database.db_manager import save_news

# ── Sentiment: lazy-loaded to avoid 438MB model load on import
_sentiment_pipe = None
_vader = None
SENTIMENT_ENGINE = None


def _get_sentiment_engine():
    global _sentiment_pipe, _vader, SENTIMENT_ENGINE
    if SENTIMENT_ENGINE is not None:
        return

    try:
        from transformers import pipeline as hf_pipeline
        _sentiment_pipe = hf_pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            truncation=True
        )
        SENTIMENT_ENGINE = "finbert"
    except Exception:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        _vader = SentimentIntensityAnalyzer()
        SENTIMENT_ENGINE = "vader"

    logger.info(f"[NewsFetcher] Sentiment engine: {SENTIMENT_ENGINE}")


# ── Scoring ───────────────────────────────────────────────────
def score_sentiment(text: str) -> float:
    """
    Returns float in [-1.0, +1.0]
      +1.0 = strongly positive (bullish signal)
      -1.0 = strongly negative (bearish signal)
       0.0 = neutral
    """
    if not text or not text.strip():
        return 0.0

    _get_sentiment_engine()

    if SENTIMENT_ENGINE == "finbert":
        result = _sentiment_pipe(text[:512])[0]
        label  = result['label'].lower()   # 'positive'/'negative'/'neutral'
        score  = result['score']           # confidence 0→1
        if label == 'positive':
            return round(score, 4)
        elif label == 'negative':
            return round(-score, 4)
        return 0.0
    else:
        scores = _vader.polarity_scores(text)
        return round(scores['compound'], 4)  # already -1 to +1


# ── Fetchers (unchanged from your original) ───────────────────
def fetch_yahoo_rss(ticker: str) -> list[dict]:
    url  = (f"https://feeds.finance.yahoo.com/rss/2.0/headline"
            f"?s={ticker}&region=US&lang=en-US")
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries[:5]:
        title = entry.get("title", "").strip()
        if not title:
            continue
        results.append({
            "ticker"     : ticker,
            "title"      : title,
            "summary"    : entry.get("summary", ""),
            "published"  : entry.get("published", ""),
            "source"     : "yahoo_rss",
            "fetched_at" : datetime.utcnow().isoformat()
        })
    return results


def fetch_newsapi(ticker: str) -> list[dict]:
    if not NEWS_API_KEY:
        return []
    url  = (
        f"https://newsapi.org/v2/everything"
        f"?q={ticker}&language=en&sortBy=publishedAt"
        f"&pageSize=5&apiKey={NEWS_API_KEY}"
    )
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return []
    return [{
        "ticker"     : ticker,
        "title"      : a.get("title", ""),
        "summary"    : a.get("content", ""),
        "published"  : a.get("publishedAt", ""),
        "source"     : "newsapi",
        "fetched_at" : datetime.utcnow().isoformat()
    } for a in resp.json().get("articles", [])]


# ── Main fetch + score ─────────────────────────────────────────
def fetch_all_news() -> pd.DataFrame:
    all_news = []
    for ticker in ACTIVE_TICKERS:
        all_news.extend(fetch_yahoo_rss(ticker))
        all_news.extend(fetch_newsapi(ticker))
        logger.info(f"[NewsFetcher] {ticker}: {len(all_news)} articles so far")

    df = pd.DataFrame(all_news).drop_duplicates(subset=["ticker", "title"])

    # ── NEW: Score every headline
    logger.info("[NewsFetcher] Scoring sentiment...")
    df['full_text'] = (df['title'].fillna('') + '. ' + df['summary'].fillna('')).str.strip('. ')
    df['sentiment_score'] = df['full_text'].apply(score_sentiment)
    df['sentiment_label'] = df['sentiment_score'].apply(
        lambda s: 'positive' if s > 0.2 else ('negative' if s < -0.2 else 'neutral')
    )

    save_news(df)
    logger.info(f"[NewsFetcher] Saved {len(df)} articles with sentiment to DB")
    return df


if __name__ == "__main__":
    df = fetch_all_news()
    print(df[['ticker', 'title', 'sentiment_score', 'sentiment_label']].to_string())
