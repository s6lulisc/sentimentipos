import pandas as pd
import pysentiment2 as ps
import pytask

from sentimentipos.analysis import get_sentiment_scores, run_linear_regression
from sentimentipos.config import BLD
from sentimentipos.data_management import ipo_tickers


@pytask.mark.depends_on(
    {
        "scripts": ["model.py"],
        "data_info": BLD / "python" / "data" / "tokenized_texts",
        "ipo_info_csv": BLD / "python" / "data",
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
        depends_on["data_info"],
    )
    sentiment_scores.to_csv(produces["models"] / "sentiment_scores.csv")
    ipo_info = pd.read_csv(depends_on["ipo_info_csv"] / "ipo_info.csv")
    ipo_info.reset_index(drop=True, inplace=True)
    sentiment_scores.reset_index(drop=True, inplace=True)
    ipo_info["returns"]
    sentiment_scores["Polarity"]
    summary_table = run_linear_regression(ipo_info, sentiment_scores)
    with open(produces["table"] / "summary_table.tex", "w") as f:
        f.write(summary_table.as_latex())
