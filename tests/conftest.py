import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_ohlcv():
    """Synthetic OHLCV data for 3 tickers, 30 trading days."""
    dates = pd.date_range("2025-01-01", periods=30, freq="B")
    records = []
    for ticker in ["AAA", "BBB", "CCC"]:
        rng = np.random.default_rng(abs(hash(ticker)) % 2**31)
        close = 100 + np.cumsum(rng.standard_normal(30) * 2)
        for i, d in enumerate(dates):
            records.append({
                "date": d,
                "ticker": ticker,
                "open": close[i] - 1,
                "high": close[i] + 1,
                "low": close[i] - 2,
                "close": close[i],
                "volume": 1_000_000,
            })
    return pd.DataFrame(records)


@pytest.fixture
def sample_returns(sample_ohlcv):
    from data.analytics import calculate_returns
    return calculate_returns(sample_ohlcv)
