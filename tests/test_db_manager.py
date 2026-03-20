import pandas as pd
import pytest
from unittest.mock import patch
from database.db_manager import save_prices, load_prices, save_news, load_news


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path):
    """Redirect all DB operations to a temporary directory."""
    db_path = str(tmp_path / "test.db")
    with patch("database.db_manager.get_connection") as mock_conn:
        import sqlite3
        conn = sqlite3.connect(db_path)
        mock_conn.return_value = conn
        yield conn
        conn.close()


def test_prices_round_trip(sample_ohlcv):
    save_prices(sample_ohlcv)
    loaded = load_prices()
    assert len(loaded) == len(sample_ohlcv)
    assert set(loaded.columns) >= {"date", "ticker", "close"}


def test_prices_dedup(sample_ohlcv):
    save_prices(sample_ohlcv)
    save_prices(sample_ohlcv)  # insert same data twice
    loaded = load_prices()
    assert len(loaded) == len(sample_ohlcv)


def test_news_round_trip():
    df = pd.DataFrame([
        {"ticker": "NVDA", "title": "Test headline", "sentiment_score": 0.5},
        {"ticker": "TSM", "title": "Another headline", "sentiment_score": -0.3},
    ])
    save_news(df)
    loaded = load_news()
    assert len(loaded) == 2
