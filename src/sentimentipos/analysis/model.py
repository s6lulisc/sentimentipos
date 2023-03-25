import pandas as pd
import statsmodels.api as sm


def get_sentiment_scores(ipo_list, lm, path):
    """Calculates sentiment scores for a list of IPO tickers using a given language
    model.

    Args:
        ipo_list (list): A list of stock tickers to calculate sentiment scores for.
        lm (LanguageModel): The language model to use for sentiment analysis.
        path (Path): The path to the directory containing the CSV files with the tokenized
            words for each company to use in the sentiment analysis.

    Returns:
        df_scores (pandas.DataFrame): A DataFrame with sentiment scores for each ticker in ipo_list.
            The DataFrame has the following columns:
            - Positive: The proportion of words with a positive sentiment score.
            - Negative: The proportion of words with a negative sentiment score.
            - Polarity: The overall polarity score (positive - negative).
            - Subjectivity: The overall subjectivity score (proportion of words with
              non-neutral sentiment).

    """
    # Initialize an empty DataFrame with the tickers as index
    df_scores = pd.DataFrame(index=ipo_list)

    # Loop through the tickers and get the scores
    for ticker in ipo_list:
        words_file = path / f"{ticker}.csv"
        words_df = pd.read_csv(words_file, header=None)
        words = list(words_df[0])

        score = lm.get_score(words)

        # Add the scores to the DataFrame
        df_scores.loc[ticker, "Positive"] = score["Positive"]
        df_scores.loc[ticker, "Negative"] = score["Negative"]
        df_scores.loc[ticker, "Polarity"] = score["Polarity"]
        df_scores.loc[ticker, "Subjectivity"] = score["Subjectivity"]

    return df_scores


def run_linear_regression(df_info, sentiment_scores):
    """Runs a linear regression model using sentiment scores as the independent variable
    and IPO first day returns as the dependent variable.

    Args:
        df_info (pandas.DataFrame): A DataFrame containing IPO information, including
            the ticker, company name, IPO date, and stock returns.
        sentiment_scores (pandas.DataFrame): A DataFrame containing sentiment scores for
            each ticker in df_info.

    Returns:
        summary_table (str): A summary table of the linear regression model.

    """
    df_info.reset_index(drop=True, inplace=True)
    sentiment_scores.reset_index(drop=True, inplace=True)
    y = df_info["returns"]
    X = sentiment_scores["Polarity"]
    model = sm.OLS(y, sm.add_constant(X)).fit()
    summary_table = model.summary()
    return summary_table
