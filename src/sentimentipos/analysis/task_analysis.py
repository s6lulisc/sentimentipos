import pysentiment2 as ps
import pytask

from sentimentipos.analysis import get_sentiment_scores
from sentimentipos.config import BLD
from sentimentipos.data_management import ipo_tickers


@pytask.mark.depends_on(
    {
        "data_info": BLD / "python" / "data" / "tokenized_texts",
    },
)
@pytask.mark.produces(
    {
        "models": BLD / "python" / "models",
    },
)
def task_get_sentiment_scores(depends_on, produces):
    """Use models/tables for regression plot, save as .png."""  ### need to rewrite this docstring
    lm = ps.LM()
    ipo_list = ipo_tickers()
    sentiment_scores = get_sentiment_scores(
        ipo_list,
        lm,
        depends_on["data_info"],
    )
    sentiment_scores.to_csv(produces["models"] / "sentiment_scores.csv")
