import pandas as pd
import statsmodels.api as sm


def get_sentiment_scores(ipo_list, lm, path):
    """Calculate sentiment scores for each ticker in the IPO list.

    Args:
        ipo_list (list): A list of ticker symbols.
        lm (SentimentIntensityAnalyzer): Instance of a sentiment analyzer.
        path (Path): Directory path containing the words files for each ticker.

    Returns:
        df_scores (pd.DataFrame): DataFrame containing sentiment scores for each ticker.

    """
    df_scores = pd.DataFrame(index=ipo_list)

    for ticker in ipo_list:
        words_file = path / f"{ticker}.csv"
        words_df = pd.read_csv(words_file, header=None)
        words = list(words_df[0])

        score = lm.get_score(words)

        df_scores.loc[ticker, "Positive"] = score["Positive"]
        df_scores.loc[ticker, "Negative"] = score["Negative"]
        df_scores.loc[ticker, "Polarity"] = score["Polarity"]
        df_scores.loc[ticker, "Subjectivity"] = score["Subjectivity"]

    return df_scores


def run_linear_regression(df_info, sentiment_scores):
    """Run a linear regression model using IPO returns and sentiment polarity scores.

    Args:
        df_info (pd.DataFrame): DataFrame containing IPO returns.
        sentiment_scores (pd.DataFrame): DataFrame containing sentiment polarity scores.

    Returns:
        summary_table (str): Summary table of the linear regression model.

    """
    df_info.reset_index(drop=True, inplace=True)
    sentiment_scores.reset_index(drop=True, inplace=True)
    y = df_info["returns"]
    X = sentiment_scores["Polarity"]
    model = sm.OLS(y, sm.add_constant(X)).fit()
    summary_table = model.summary()
    return summary_table
