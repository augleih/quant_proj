# import sqlite3
# import pandas as pd
# import numpy as np
# from scipy import stats
# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from config.settings import DB_PATH

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# db_path = os.path.join(BASE_DIR, DB_PATH)
# conn = sqlite3.connect(db_path)
# df = pd.read_sql("SELECT date, ticker, close FROM prices", conn, parse_dates=["date"])
# conn.close()

# prices = df.pivot(index="date", columns="ticker", values="close").astype(float)
# log_returns = np.log(prices / prices.shift(1)).dropna()

# stats_list = []
# for ticker in log_returns.columns:
#     r = log_returns[ticker].dropna()
#     jb_stat, jb_p = stats.jarque_bera(r)
#     stats_list.append({
#         "ticker": ticker,
#         "annual_return": round(r.mean() * 252, 4),
#         "annual_vol": round(r.std() * np.sqrt(252), 4),
#         "skewness": round(stats.skew(r), 3),
#         "kurtosis": round(stats.kurtosis(r) + 3, 3),
#         "is_normal_p": round(jb_p, 4),
#     })

# df_stats = pd.DataFrame(stats_list).sort_values("annual_return", ascending=False)

# print("=" * 65)
# print("RETURN DISTRIBUTION ANALYSIS - TOP 50 S&P 500")
# print("=" * 65)
# print(df_stats.to_string(index=False))
# print(f"\nAvg kurtosis: {df_stats['kurtosis'].mean():.2f} (normal = 3.0)")
# print(f"Avg skewness: {df_stats['skewness'].mean():.3f} (normal = 0.0)")
# print(f"Tickers w/ fat tail: {(df_stats['kurtosis'] > 3).sum()} / {len(df_stats)}")
# print(f"Non-normal tickers: {(df_stats['is_normal_p'] < 0.05).sum()} / {len(df_stats)}")

# os.makedirs("research/outputs", exist_ok=True)
# df_stats.to_csv("research/outputs/stage1_distribution_stats.csv", index=False)
# print("\n Saved distribution stats to research/outputs/stage1_distribution_stats.csv")

import yfinance as yf
import numpy as np
from scipy import stats

aapl = yf.download("AAPL", period="2y", auto_adjust=True, progress=False)
prices = aapl["Close"].squeeze().astype(float)
returns = prices.pct_change().dropna()

mean = returns.mean()
std = returns.std()
skew = stats.skew(returns)
kurt = stats.kurtosis(returns) + 3

print(f"Mean daily return: {mean*100:.3f}%")
print(f"Standard deviation: {std*100:.3f}%")
print(f"Skewness: {skew:.3f} (0 = symmetric, negative = crash-prone)")
print(f"Kurtosis: {kurt:.3f} (3.0 = normal, higher = fatter tails)")

print("\nReturn Distribution (text histogram):")
counts, bins = np.histogram(returns * 100, bins=20)

for i, count in enumerate(counts):
    label = f"{bins[i]:+.1f}%"
    bar = "#" * (count // 2)
    print(f" {label:>7} | {bar} ({count})")