import argparse
from config.logging import logger


def stage_prices():
    from data.price_fetcher import fetch_prices
    logger.info("Stage: Price Fetch")
    return fetch_prices()


def stage_analytics(ohlcv_df=None):
    from data.analytics import calculate_returns, risk_metrics, correlation_matrix
    if ohlcv_df is None:
        from database.db_manager import load_prices
        ohlcv_df = load_prices()
    logger.info("Stage: Analytics")
    returns = calculate_returns(ohlcv_df)
    dashboard = risk_metrics(returns)
    corr = correlation_matrix(returns)
    logger.info(f"Risk Dashboard:\n{dashboard.to_string()}")
    logger.info(f"Correlation Matrix:\n{corr.to_string()}")
    return dashboard, corr


def stage_news():
    from data.news_fetcher import fetch_all_news
    logger.info("Stage: News + Sentiment")
    news_df = fetch_all_news()
    logger.info(f"\n{news_df[['ticker', 'sentiment_score', 'sentiment_label']].head(10)}")
    return news_df


def run_pipeline(stages=None):
    if stages is None:
        stages = ["prices", "analytics", "news"]

    ohlcv_df = None
    if "prices" in stages:
        ohlcv_df = stage_prices()
    if "analytics" in stages:
        stage_analytics(ohlcv_df)
    if "news" in stages:
        stage_news()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quant Trading Pipeline")
    parser.add_argument(
        "--stages", nargs="+",
        choices=["prices", "analytics", "news"],
        default=None,
        help="Run specific stages (default: all)"
    )
    args = parser.parse_args()
    run_pipeline(args.stages)
