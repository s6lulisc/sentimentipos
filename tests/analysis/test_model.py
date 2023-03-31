import numpy as np
import pandas as pd
import pytest
from sentimentipos.analysis.model import get_sentiment_scores, run_linear_regression
from statsmodels import api as sm


class TestLanguageModel:
    @pytest.fixture(scope="class")
    def ipo_list(self):
        return ["AAPL", "MSFT"]

    @pytest.fixture(scope="class")
    def example_lm(self):
        class ExampleLanguageModel:
            def get_score(self, words):
                return {
                    "Positive": 0.2,
                    "Negative": 0.1,
                    "Polarity": 0.1,
                    "Subjectivity": 0.3,
                }

        return ExampleLanguageModel()

    @pytest.fixture(scope="class")
    def example_path(self, tmp_path_factory):
        path = tmp_path_factory.mktemp("data")
        for ticker in ["AAPL", "MSFT"]:
            words_file = path / f"{ticker}.csv"
            words = ["word1", "word2", "word3"]
            pd.DataFrame(words).to_csv(words_file, header=None, index=None)
        return path

    def test_get_sentiment_scores(self, ipo_list, example_lm, example_path):
        expected = pd.DataFrame(
            {
                "Positive": [0.2, 0.2],
                "Negative": [0.1, 0.1],
                "Polarity": [0.1, 0.1],
                "Subjectivity": [0.3, 0.3],
            },
            index=ipo_list,
        )
        result = get_sentiment_scores(ipo_list, example_lm, example_path)
        pd.testing.assert_frame_equal(result, expected)

    def test_run_linear_regression(self):
        df_info = pd.DataFrame({"returns": np.random.rand(8)})
        sentiment_scores = pd.DataFrame({"Polarity": np.random.rand(8)})
        result = run_linear_regression(df_info, sentiment_scores)
        assert isinstance(
            result,
            sm.regression.linear_model.RegressionResultsWrapper,
        ), "The result should be an instance of statsmodels.regression.linear_model.RegressionResultsWrapper."
