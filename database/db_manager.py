import sqlite3
import pandas as pd
from config.settings import DB_PATH
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_connection():
    db_path = os.path.join(BASE_DIR, DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def save_prices(df: pd.DataFrame):
    with get_connection() as conn:
        df.to_sql('prices', conn, if_exists="append", index=False)
        conn.execute("""
            DELETE FROM prices
            WHERE rowid NOT IN (
                SELECT MAX(rowid)
                FROM prices
                GROUP BY date, ticker
            )
        """)

def load_prices(ticker: str = None) -> pd.DataFrame:
    with get_connection() as conn:
        if ticker:
            df = pd.read_sql("SELECT * FROM prices WHERE ticker = ?", conn, params=[ticker], parse_dates=["date"])
        else:
            df = pd.read_sql("SELECT * FROM prices", conn, parse_dates=["date"])
    return df

def save_news(df: pd.DataFrame):
    with get_connection() as conn:
        df.to_sql('news', conn, if_exists="append", index=False)
        conn.execute("""
            DELETE FROM news
            WHERE rowid NOT IN (
                SELECT MAX(rowid)
                FROM news
                GROUP BY ticker, title
            )
        """)
    
def load_news() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM news", conn)