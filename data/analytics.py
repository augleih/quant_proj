import pandas as pd
import numpy as np
from config.settings import RISK_FREE_RATE, TRADING_DAYS


def calculate_returns(ohlcv_df: pd.DataFrame) -> pd.DataFrame:
    pivot = ohlcv_df.pivot(index='date', columns='ticker', values='close')
    return pivot.pct_change().dropna()


def risk_metrics(returns: pd.DataFrame) -> pd.DataFrame:
    rf, td = RISK_FREE_RATE, TRADING_DAYS
    results = {}

    for ticker in returns.columns:
        r = returns[ticker].dropna()
        ann_ret = r.mean() * td
        tot_std = r.std() * np.sqrt(td)
        neg_r = r[r < 0]
        dn_std = neg_r.std() * np.sqrt(td) if len(neg_r) > 1 else np.nan
        sharpe = (ann_ret - rf) / tot_std
        sortino = (ann_ret - rf) / dn_std if dn_std else np.nan
        cum = (1 + r).cumprod()
        mdd = ((cum - cum.cummax()) / cum.cummax()).min()
        var_95 = np.percentile(r, 5)

        results[ticker] = {
            "Annual Return %": round(ann_ret * 100, 2),
            "Sharpe": round(sharpe, 2),
            "Sortino": round(sortino, 2),
            "MDD %": round(mdd * 100, 2),
            "VaR 95%": round(var_95 * 100, 2),
        }
    return pd.DataFrame(results).T


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr().round(2)
