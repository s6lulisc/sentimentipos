########## our code

import pandas as pd
import pysentiment2 as ps
import pytask

from sentimentipos.analysis import get_sentiment_scores, run_linear_regression
from sentimentipos.config import BLD
from sentimentipos.data_management import ipo_tickers


@pytask.mark.depends_on(
    {
        "scripts": ["model.py"],
        "data_info": BLD / "python" / "data",
    },
)
@pytask.mark.produces(
    {"models": BLD / "python" / "models", "table": BLD / "python" / "tables"},
)
def task_get_sentiment_scores(depends_on, produces):
    """"""
    lm = ps.LM()
    ipo_list = ipo_tickers()
    sentiment_scores = get_sentiment_scores(
        ipo_list,
        lm,
        depends_on["data_info"] / "tokenized_texts",
    )
    sentiment_scores.to_csv(produces["models"] / "sentiment_scores.csv")
    #######################
    # Specify the dependent variable and independent variable
    df_info = pd.read_csv(depends_on["data_info"] / "df_info.csv")
    # Reset index and select columns for X and y
    df_info.reset_index(drop=True, inplace=True)
    sentiment_scores.reset_index(drop=True, inplace=True)
    df_info["returns"]
    sentiment_scores["Polarity"]
    # Fit a linear regression model
    summary_table = run_linear_regression(df_info, sentiment_scores)
    with open(produces["table"] / "summary_table.tex", "w") as f:
        f.write(summary_table.as_latex())
