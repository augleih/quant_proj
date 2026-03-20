import numpy as np
from data.analytics import calculate_returns, risk_metrics, correlation_matrix


def test_calculate_returns_shape(sample_ohlcv):
    returns = calculate_returns(sample_ohlcv)
    assert returns.shape == (29, 3)  # 30 days - 1, 3 tickers
    assert set(returns.columns) == {"AAA", "BBB", "CCC"}


def test_calculate_returns_no_nan(sample_ohlcv):
    returns = calculate_returns(sample_ohlcv)
    assert not returns.isna().any().any()


def test_risk_metrics_columns(sample_returns):
    dashboard = risk_metrics(sample_returns)
    expected_cols = {"Annual Return %", "Sharpe", "Sortino", "MDD %", "VaR 95%"}
    assert set(dashboard.columns) == expected_cols


def test_risk_metrics_all_tickers(sample_returns):
    dashboard = risk_metrics(sample_returns)
    assert set(dashboard.index) == {"AAA", "BBB", "CCC"}


def test_risk_metrics_finite(sample_returns):
    dashboard = risk_metrics(sample_returns)
    assert np.isfinite(dashboard["Sharpe"]).all()
    assert np.isfinite(dashboard["MDD %"]).all()


def test_correlation_matrix_symmetric(sample_returns):
    corr = correlation_matrix(sample_returns)
    assert corr.shape == (3, 3)
    # diagonal is 1.0
    assert (np.diag(corr.values) == 1.0).all()
    # symmetric
    assert (corr.values == corr.values.T).all()
    # values in [-1, 1]
    assert (corr.values >= -1).all() and (corr.values <= 1).all()
