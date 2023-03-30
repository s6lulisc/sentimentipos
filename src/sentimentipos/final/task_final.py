import matplotlib.pyplot as plt
import pandas as pd
import pytask
import statsmodels.api as sm

from sentimentipos.analysis import run_linear_regression
from sentimentipos.config import BLD
from sentimentipos.final import plot_regression


@pytask.mark.depends_on(
    {
        "models": BLD / "python" / "models",
        "data": BLD / "python" / "data",
    },
)
@pytask.mark.produces(
    {
        "figures": BLD / "python" / "figures",
        "tables": BLD / "python" / "tables",
    },
)
def task_regression_plot(depends_on, produces):
    sentiment_scores = pd.read_csv(depends_on["models"] / "sentiment_scores.csv")
    ipo_info = pd.read_csv(depends_on["data"] / "ipo_info.csv")
    summary_table = run_linear_regression(ipo_info, sentiment_scores)
    with open(produces["tables"] / "summary_table.tex", "w") as f:
        f.write(summary_table.as_latex())

    y = ipo_info["returns"]
    X = sentiment_scores["Polarity"]
    model = sm.OLS(y, sm.add_constant(X)).fit()
    plot_regression(X, y, model, ipo_info)
    plt.savefig(produces["figures"] / "regression_plot.png")
