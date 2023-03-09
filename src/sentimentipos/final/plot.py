import matplotlib.pyplot as plt
import statsmodels.api as sm

# Functions plotting results


def plot_regression(X, y, model):
    # Plot the data points
    plt.scatter(X, y)

    # Add the regression line
    plt.plot(X, model.predict(sm.add_constant(X)), color="red")

    # Add axis labels and title
    plt.xlabel("Sentiment Scores")
    plt.ylabel("Returns")
    plt.title("Linear Regression Model")
