import matplotlib.pyplot as plt
import statsmodels.api as sm


def plot_regression(X, y, model, data):
    """Plots a linear regression model using the sentiment scores on the X axis (as
    independent variable) and the IPO first day returns on the y axis (as the dependent
    variable).

    Args:
    X (float): the independent variable, the sentiment scores.
    y (float): The dependent variable, the first day returns.
    model (statsmodels.regression.linear_model.RegressionResultsWrapper): The linear regression model to plot.

    """
    # Create a larger figure
    plt.figure(figsize=(12, 8))

    # Plot the data points
    plt.scatter(X, y, label="Data points", alpha=0.7, marker="o", s=50, edgecolors="k")

    # Add the regression line
    plt.plot(
        X,
        model.predict(sm.add_constant(X)),
        color="green",
        label="Regression line",
    )

    # Add axis labels and title
    plt.xlabel("Sentiment Scores", fontsize=16)
    plt.ylabel("Returns", fontsize=16)
    plt.title("Linear Regression Model", fontsize=20)

    # Add company labels to the data points with an offset to prevent overlapping
    for i, company_name in enumerate(data["company_name"]):
        plt.annotate(
            company_name,
            (X.iloc[i], y.iloc[i]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=12,
        )

    # Add a legend
    plt.legend(fontsize=12)
