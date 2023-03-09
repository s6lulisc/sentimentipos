import pandas as pd
import statsmodels.api as sm


def get_sentiment_scores(ipo_list, lm, path):
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
    # Concatenate X and y into a single DataFrame
    # Print the model summary
    df_info.reset_index(drop=True, inplace=True)
    sentiment_scores.reset_index(drop=True, inplace=True)
    y = df_info["returns"]
    X = sentiment_scores["Polarity"]
    model = sm.OLS(y, sm.add_constant(X)).fit()
    summary_table = model.summary()
    return summary_table
