########## our code

import pandas as pd
import pysentiment2 as ps
import pytask
import statsmodels.api as sm

from sentimentipos.analysis import get_sentiment_scores
from sentimentipos.config import BLD, SRC
from sentimentipos.data_management import ipo_tickers


@pytask.mark.depends_on(
    {
        "scripts": ["model.py"],
        "data": BLD / "python" / "data",
        "data_info": SRC / "data_management" / "data_info.yaml",
    },
)
@pytask.mark.produces(
    {"models": BLD / "python" / "models", "tables": BLD / "python" / "tables"},
)
def task_get_sentiment_scores(depends_on, produces):
    """"""
    lm = ps.LM()
    ipo_list = ipo_tickers()
    sentiment_scores = get_sentiment_scores(ipo_list, lm, depends_on["data"])
    sentiment_scores.to_csv(produces["models"] / "sentiment_scores.csv")
    #######################
    # Specify the dependent variable and independent variable
    df_info = pd.read_csv(depends_on["data"] / "df_info.csv")
    df_info.reset_index(drop=True, inplace=True)
    sentiment_scores.reset_index(drop=True, inplace=True)
    y = df_info["returns"]
    X = sentiment_scores["Polarity"]
    # Fit a linear regression model
    model = sm.OLS(y, X).fit()
    # Print the summary of the model
    model.summary()
