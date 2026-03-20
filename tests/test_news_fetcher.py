from unittest.mock import patch, MagicMock


def test_score_sentiment_empty():
    from data.news_fetcher import score_sentiment
    assert score_sentiment("") == 0.0
    assert score_sentiment(None) == 0.0
    assert score_sentiment("   ") == 0.0


@patch("data.news_fetcher._sentiment_pipe")
@patch("data.news_fetcher.SENTIMENT_ENGINE", "finbert")
def test_score_sentiment_positive(mock_pipe):
    mock_pipe.return_value = [{"label": "positive", "score": 0.95}]
    from data.news_fetcher import score_sentiment
    result = score_sentiment("great earnings beat expectations")
    assert result > 0


@patch("data.news_fetcher._sentiment_pipe")
@patch("data.news_fetcher.SENTIMENT_ENGINE", "finbert")
def test_score_sentiment_negative(mock_pipe):
    mock_pipe.return_value = [{"label": "negative", "score": 0.88}]
    from data.news_fetcher import score_sentiment
    result = score_sentiment("stock crashes on weak guidance")
    assert result < 0


@patch("data.news_fetcher._sentiment_pipe")
@patch("data.news_fetcher.SENTIMENT_ENGINE", "finbert")
def test_score_sentiment_neutral(mock_pipe):
    mock_pipe.return_value = [{"label": "neutral", "score": 0.70}]
    from data.news_fetcher import score_sentiment
    result = score_sentiment("company to present at conference")
    assert result == 0.0
