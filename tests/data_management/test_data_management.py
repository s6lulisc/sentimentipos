import json
import os
import zipfile

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from sentimentipos.data_management.clean_data import (
    unzipper,
)
from sentimentipos.data_management.data_processing import (
    contains_word,
    filter_and_store_df_by_ipo_date,
    filter_df_by_ipo_date,
    get_ipo_info,
    get_matching_files,
    split_text,
)


def test_unzipper(tmpdir):
    zip_file_path = tmpdir.join("test.zip")
    text_file_path = tmpdir.join("test.txt")

    with open(text_file_path, "w") as f:
        f.write("IPO underpricing")

    with zipfile.ZipFile(zip_file_path, "w") as zf:
        zf.write(text_file_path, "test.txt")

    unzipper(zip_file_path, tmpdir)

    extracted_file_path = tmpdir.join("test.txt")
    assert os.path.exists(extracted_file_path)

    with open(extracted_file_path) as f:
        content = f.read()

    assert content == "IPO underpricing"


@pytest.fixture()
def _create_mock_ipo_data_clean():
    data = {
        "trade_date": [
            "2018-02-20",
            "2018-04-05",
            "2018-06-12",
            "2018-08-24",
        ],
        "company": [
            "Company A",
            "Company B",
            "Company C",
            "Company D",
        ],
        "ticker": [
            "COMA",
            "COMB",
            "COMC",
            "COMD",
        ],
        "offr_price": [
            25,
            15,
            20,
            18,
        ],
        "open_price": [
            30.20,
            16.90,
            21.50,
            19.60,
        ],
        "1st_day_close": [
            33.35,
            11.25,
            23.70,
            17.45,
        ],
        "open_prc_pct_rtrn": [
            0.104,
            -0.292,
            0.075,
            -0.078,
        ],
    }
    df = pd.DataFrame(data)
    df["offr_price"] = df["offr_price"].astype("int64")
    df["open_price"] = df["open_price"].astype("float64")
    df["1st_day_close"] = df["1st_day_close"].astype("float64")
    df["open_prc_pct_rtrn"] = df["open_prc_pct_rtrn"].astype("float64")
    return df


@pytest.fixture()
def clean_data(_create_mock_ipo_data_clean):
    return _create_mock_ipo_data_clean


def test_get_ipo_info(clean_data):
    ipo_list = ["COMA", "COMB", "COMC", "COMD"]
    expected_ipo_info = {
        "COMA": {
            "company_name": "Company A",
            "ticker": "COMA",
            "ipo_date": "2018-02-20",
            "returns": 0.104,
        },
        "COMB": {
            "company_name": "Company B",
            "ticker": "COMB",
            "ipo_date": "2018-04-05",
            "returns": -0.292,
        },
        "COMC": {
            "company_name": "Company C",
            "ticker": "COMC",
            "ipo_date": "2018-06-12",
            "returns": 0.075,
        },
        "COMD": {
            "company_name": "Company D",
            "ticker": "COMD",
            "ipo_date": "2018-08-24",
            "returns": -0.078,
        },
    }
    expected_ipo_info = pd.DataFrame.from_dict(expected_ipo_info, orient="index")
    actual_ipo_info = get_ipo_info(ipo_list, clean_data)
    pd.testing.assert_frame_equal(expected_ipo_info, actual_ipo_info)


def test_contains_word(tmpdir):
    test_json_file = tmpdir.join("test.json")
    test_word = "Economics"

    json_data = {
        "title": f"The Importance of {test_word} in the Modern World",
        "content": "This is a sample article about economics.",
    }

    with open(test_json_file, "w") as f:
        json.dump(json_data, f)

    assert contains_word(test_json_file, test_word) is True
    assert contains_word(test_json_file, "NonExistentWord") is False


def test_get_matching_files(tmpdir):
    target_word = "IPO"
    file_contents = [
        {"title": "IPO underpricing"},
        {"title": "Title without the target word"},
        {"title": "Another title with target_word IPO"},
    ]

    for i, content in enumerate(file_contents):
        file_path = tmpdir.join(f"file_{i}.json")
        with open(file_path, "w") as f:
            json.dump(content, f)

    matching_files = get_matching_files(tmpdir, target_word)

    assert len(matching_files) == 2

    for file_path in matching_files:
        with open(file_path) as f:
            data = json.load(f)
        assert target_word in data["title"]


def test_filter_df_by_ipo_date():
    # Sample Data
    ipo_info = pd.DataFrame(
        {
            "company_name": ["Company A", "Company B"],
            "ticker": ["A", "B"],
            "ipo_date": ["2020-01-15", "2020-02-15"],
            "first_day_return": [0.1, 0.2],
        },
    ).set_index("ticker")

    df_A = pd.DataFrame(
        {
            "published": ["2020-01-01", "2020-01-10", "2020-01-20"],
            "content": ["Article 1", "Article 2", "Article 3"],
        },
    )

    df_B = pd.DataFrame(
        {
            "published": ["2020-02-01", "2020-02-10", "2020-02-20"],
            "content": ["Article 4", "Article 5", "Article 6"],
        },
    )

    df_dict = {"df_Company A": df_A, "df_Company B": df_B}

    # Test cases
    result_A = filter_df_by_ipo_date(df_dict, "Company A", "A", ipo_info)
    result_B = filter_df_by_ipo_date(df_dict, "Company B", "B", ipo_info)

    assert isinstance(result_A, pd.DataFrame), "The result should be a DataFrame."
    assert isinstance(result_B, pd.DataFrame), "The result should be a DataFrame."

    expected_A = df_A[df_A["published"] < ipo_info.loc["A", "ipo_date"]]
    expected_B = df_B[df_B["published"] < ipo_info.loc["B", "ipo_date"]]

    assert result_A.equals(
        expected_A,
    ), "The filtered dataframe for Company A should match the expected dataframe."
    assert result_B.equals(
        expected_B,
    ), "The filtered dataframe for Company B should match the expected dataframe."


def test_filter_and_store_df_by_ipo_date():
    # Sample Data
    ipo_info = pd.DataFrame(
        {
            "company_name": ["Company A", "Company B"],
            "ticker": ["A", "B"],
            "ipo_date": ["2020-01-15", "2020-02-15"],
            "first_day_return": [0.1, 0.2],
        },
    ).set_index("ticker")

    df_A = pd.DataFrame(
        {
            "published": ["2020-01-01", "2020-01-10", "2020-01-20"],
            "content": ["Article 1", "Article 2", "Article 3"],
        },
    )

    df_B = pd.DataFrame(
        {
            "published": ["2020-02-01", "2020-02-10", "2020-02-20"],
            "content": ["Article 4", "Article 5", "Article 6"],
        },
    )

    df_dict = {"df_Company A": df_A, "df_Company B": df_B}
    result = filter_and_store_df_by_ipo_date(ipo_info, df_dict)
    assert isinstance(result, dict), "The result should be a dictionary."
    assert len(result) == 2, "There should be two filtered dataframes in the result."
    assert "df_A" in result, "The result should contain a key 'df_A'."
    assert "df_B" in result, "The result should contain a key 'df_B'."
    assert result["df_A"].equals(
        df_A[df_A["published"] < ipo_info.loc["A", "ipo_date"]],
    ), "The 'df_A' value should be equal to the filtered df_A."
    assert result["df_B"].equals(
        df_B[df_B["published"] < ipo_info.loc["B", "ipo_date"]],
    ), "The 'df_B' value should be equal to the filtered df_B."


def test_split_text():
    expected_words_df = pd.DataFrame(
        {"words": ["IPO", "underpricing", "test", "sentence"]},
    )
    df = pd.DataFrame({"text": ["IPO underpricing test sentence"]})
    words_df = split_text(df)

    assert_frame_equal(expected_words_df, words_df)
