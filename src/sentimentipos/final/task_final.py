import matplotlib.pyplot as plt
import pandas as pd
import pytask

from sentimentipos.analysis import run_linear_regression
from sentimentipos.config import BLD
from sentimentipos.final import plot_regression


@pytask.mark.depends_on(
    {
        "models": BLD / "python" / "models" / "sentiment_scores.csv",
        "ipo_info_data": BLD / "python" / "data" / "ipo_info.csv",
    },
)
@pytask.mark.produces(
    {
        "figures": BLD / "python" / "figures" / "regression_plot.png",
        "tables": BLD / "python" / "tables",
    },
)
def task_regression_figure_table(depends_on, produces):
    """Saves regression summary table as a LaTeX file and plots the model."""
    sentiment_scores = pd.read_csv(depends_on["models"])
    ipo_info = pd.read_csv(depends_on["ipo_info_data"])
    model = run_linear_regression(ipo_info, sentiment_scores)
    y = ipo_info["returns"]
    X = sentiment_scores["Polarity"]
    plot_regression(X, y, model, ipo_info)
    plt.savefig(produces["figures"])

    summary_table = model.summary()
    with open(produces["tables"] / "summary_table.tex", "w") as f:
        f.write(summary_table.as_latex())
