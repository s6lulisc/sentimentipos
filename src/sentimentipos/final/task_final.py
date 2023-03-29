import matplotlib.pyplot as plt
import pandas as pd
import pysentiment2 as ps
import pytask
import statsmodels.api as sm

from sentimentipos.analysis import get_sentiment_scores, run_linear_regression
from sentimentipos.config import BLD
from sentimentipos.data_management import ipo_tickers
from sentimentipos.final import plot_regression


@pytask.mark.depends_on(
    {
        "scripts": ["plot.py"],
        "tables": BLD / "python" / "tables",
        "models": BLD / "python" / "models",
        "data": BLD / "python" / "data",
        "tokenized_texts": BLD / "python" / "data" / "tokenized_texts",
    },
)
@pytask.mark.produces(
    {"figures": BLD / "python" / "figures"},
)
def task_regression_plot(depends_on, produces):
    lm = ps.LM()
    ipo_list = ipo_tickers()
    sentiment_scores = get_sentiment_scores(
        ipo_list,
        lm,
        depends_on["tokenized_texts"],
    )
    ipo_info = pd.read_csv(depends_on["data"] / "ipo_info.csv")
    ipo_info.reset_index(drop=True, inplace=True)
    sentiment_scores.reset_index(drop=True, inplace=True)
    y = ipo_info["returns"]
    X = sentiment_scores["Polarity"]
    run_linear_regression(ipo_info, sentiment_scores)
    model = sm.OLS(y, sm.add_constant(X)).fit()
    plot_regression(X, y, model, ipo_info)
    plt.savefig(produces["figures"] / "regression_plot.png")
