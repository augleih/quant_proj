import sqlite3
import pandas as pd
from config.settings import DB_PATH
import os

def get_connection():
    os.makedirs("db", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def save_prices(df: pd.DataFrame):
    with get_connection() as conn:
        df.to_sql('prices', conn, if_exists="replace", index=True)

def load_prices() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM prices", conn, index_col="Date", parse_dates=["Date"])

def save_news(df: pd.DataFrame):
    with get_connection() as conn:
        with get_connection() as conn:
            df.to_sql('news', conn, if_exists="replace", index=False)
    
def load_news() -> pd.DataFrame:
    with get_connection() as aconn:
        return pd.read_sql("SELECT * FROM news", conn)