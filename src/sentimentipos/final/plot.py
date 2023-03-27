import matplotlib.pyplot as plt
import statsmodels.api as sm

# Functions plotting results


def plot_regression(X, y, model, data):
    """Plots a linear regression model using the sentiment scores on the X axis (as
    independent variable) and the IPO first day returns on the y axis (as the dependent
    variable).

    Args:
    X (float): the independent variable, the sentiment scores.
    y (float): The dependent variable, the first day returns.
    model (statsmodels.regression.linear_model.RegressionResultsWrapper): The linear regression model to plot.

    """
    # Plot the data points
    plt.scatter(X, y, label=data["company_name"])

    # Add the regression line
    plt.plot(X, model.predict(sm.add_constant(X)), color="red")

    # Add axis labels and title
    plt.xlabel("Sentiment Scores")
    plt.ylabel("Returns")
    plt.title("Linear Regression Model")
