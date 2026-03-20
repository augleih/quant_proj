# signals/sentiment_signal.py
from __future__ import annotations

import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from config.settings import SENTIMENT_LOOKBACK_DAYS  # add to settings: default 7
from database.db_manager import get_news  # assumes: get_news(ticker, days) -> DataFrame
                                          # columns: published_at, title, summary, ticker

warnings.filterwarnings("ignore")

# ── Model (loaded once at module level) ──────────────────────────────────────
_MODEL_NAME = "ProsusAI/finbert"
_tokenizer  = None
_model      = None

def _load_model():
    global _tokenizer, _model
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        _model     = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
        _model.eval()

# ── Core scoring ─────────────────────────────────────────────────────────────
def _score_texts(texts: list[str]) -> list[float]:
    """Return P(pos) - P(neg) for each text.  Range: -1.0 ~ +1.0"""
    if not texts:
        return []
    _load_model()
    inputs = _tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )
    with torch.no_grad():
        logits = _model(**inputs).logits          # shape: (N, 3)
    probs = torch.softmax(logits, dim=-1).numpy() # [positive, negative, neutral]
    # FinBERT label order: positive=0, negative=1, neutral=2
    return (probs[:, 0] - probs[:, 1]).tolist()


def _score_article(title: str, summary: str) -> float:
    """Weighted score: title 0.3 / summary 0.7"""
    scores = _score_texts([title, summary])
    if not scores or len(scores) < 2:
        return 0.0
    return 0.3 * scores[0] + 0.7 * scores[1]


# ── Per-ticker aggregation ────────────────────────────────────────────────────
def _aggregate_scores(news_df: pd.DataFrame) -> float:
    """Recency-weighted mean.  Newer articles get higher weight (linear decay)."""
    if news_df.empty:
        return 0.0

    news_df = news_df.copy()
    news_df["published_at"] = pd.to_datetime(news_df["published_at"])
    news_df = news_df.sort_values("published_at")

    # individual article scores
    news_df["raw_score"] = [
        _score_article(
            str(row.title)   if pd.notna(row.title)   else "",
            str(row.summary) if pd.notna(row.summary) else "",
        )
        for row in news_df.itertuples()
    ]

    # linear recency weights: oldest=1, newest=N
    n = len(news_df)
    weights = np.arange(1, n + 1, dtype=float)
    weights /= weights.sum()

    return float(np.dot(weights, news_df["raw_score"].values))


# ── Public API (mirrors momentum.py) ─────────────────────────────────────────
def run_sentiment_signals(
    tickers: list[str],
    days: int = 7,
) -> pd.DataFrame:
    """
    Returns DataFrame sorted by score descending.
    Columns: ticker, article_count, raw_mean, score (-1.0~+1.0), label
    """
    records = []

    for ticker in tickers:
        try:
            news_df = get_news(ticker, days=days)
        except Exception as e:
            print(f"[WARN] {ticker}: news fetch failed — {e}")
            news_df = pd.DataFrame()

        score        = _aggregate_scores(news_df)
        article_count = len(news_df)

        records.append({
            "ticker":        ticker,
            "article_count": article_count,
            "score":         round(score, 4),
            "label":         label_signal(score),
        })

    df = pd.DataFrame(records).sort_values("score", ascending=False).reset_index(drop=True)
    return df


def label_signal(score: float) -> str:
    """Shared label scale — identical to momentum.py"""
    if   score >= 0.6:  return "STRONG BUY"
    elif score >= 0.3:  return "BUY"
    elif score >= 0.1:  return "WEAK BUY"
    elif score >= -0.1: return "NEUTRAL"
    elif score >= -0.3: return "WEAK SELL"
    elif score >= -0.6: return "SELL"
    else:               return "STRONG SELL"