import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal
from sentimentipos.data_management.clean_data import (
    get_ipo_data_clean,
    unzipper,
)
from sentimentipos.data_management.data_processing import (
    contains_word,
    filter_and_store_df_by_ipo_date,
    filter_df_by_ipo_date,
    generate_dataframes,
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


TEST_DATA_FILE_PATH = "src/sentimentipos/data/original_ipo_data.xlsx"


def _create_expected_ipo_data_clean():
    data = {
        "trade_date": [
            "2018-03-23",
            "2018-04-27",
            "2018-05-04",
            "2018-05-10",
            "2018-04-03",
        ],
        "company": [
            "Dropbox",
            "Smartsheet",
            "Carbon Black",
            "AXA",
            "Spotify",
        ],
        "ticker": [
            "DBX",
            "SMAR",
            "CBLK",
            "EQH",
            "SPOT",
        ],
        "offr_price": [
            21,
            15,
            19,
            20,
            132,
        ],
        "open_price": [
            29,
            18.40,
            24.70,
            19.75,
            165.90,
        ],
        "1st_day_close": [
            28.48,
            19.50,
            23.94,
            20.34,
            149.01,
        ],
        "open_prc_pct_rtrn": [
            -0.018,
            0.060,
            -0.031,
            0.030,
            -0.102,
        ],
    }
    df = pd.DataFrame(data)
    df["offr_price"] = df["offr_price"].astype("int64")
    df["open_price"] = df["open_price"].astype("float64")
    df["1st_day_close"] = df["1st_day_close"].astype("float64")
    df["open_prc_pct_rtrn"] = df["open_prc_pct_rtrn"].astype("float64")
    return df


def test_get_ipo_data_clean():
    expected_ipo_data_clean = _create_expected_ipo_data_clean()

    actual_ipo_data_clean = get_ipo_data_clean(TEST_DATA_FILE_PATH)
    actual_ipo_data_clean = actual_ipo_data_clean[
        actual_ipo_data_clean["company"].isin(expected_ipo_data_clean["company"])
    ].reset_index(drop=True)

    assert_frame_equal(expected_ipo_data_clean, actual_ipo_data_clean)


def _create_expected_ipo_info(ipo_list):
    expected_ipo_info = {
        "DBX": {
            "company_name": "Dropbox",
            "ipo_date": "2018-03-23",
            "returns": -0.018,
        },
        "SMAR": {
            "company_name": "Smartsheet",
            "ipo_date": "2018-04-27",
            "returns": 0.060,
        },
        "CBLK": {
            "company_name": "Carbon Black",
            "ipo_date": "2018-05-04",
            "returns": -0.031,
        },
        "EQH": {
            "company_name": "AXA",
            "ipo_date": "2018-05-10",
            "returns": 0.030,
        },
        "SPOT": {
            "company_name": "Spotify",
            "ipo_date": "2018-04-03",
            "returns": -0.102,
        },
    }
    return {ticker: expected_ipo_info[ticker] for ticker in ipo_list}


def test_get_ipo_info():
    ipo_list = ["DBX", "SMAR", "CBLK", "EQH", "SPOT"]
    expected_ipo_info = _create_expected_ipo_info(ipo_list)
    actual_ipo_info = get_ipo_info(ipo_list)

    assert (
        actual_ipo_info == expected_ipo_info
    ), f"Expected {expected_ipo_info}, but got {actual_ipo_info}"


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


def _create_test_files():
    test_files = {
        "Dropbox": {"title": "Dropbox announces their IPO"},
        "Smartsheet": {"title": "Smartsheet decides to go public with IPO"},
        "Carbon Black": {"title": "Carbon Black intends to go public thorough IPO"},
        "AXA": {"title": "AXA is one week away from IPO"},
        "Spotify": {"title": "Spotify goes public"},
    }

    temp_folder = tempfile.mkdtemp()

    for company, data in test_files.items():
        with open(os.path.join(temp_folder, f"{company}.json"), "w") as f:
            json.dump(data, f)

    return temp_folder


def _delete_test_files(temp_folder):
    shutil.rmtree(temp_folder)


def _create_expected_df_dict(ipo_list):
    expected_df_dict = {}
    for ticker in ipo_list:
        company_name = {
            "DBX": "Dropbox",
            "SMAR": "Smartsheet",
            "CBLK": "Carbon Black",
            "EQH": "AXA",
            "SPOT": "Spotify",
        }[ticker]

        data = {
            "title": [f"{company_name}"],
        }

        df = pd.DataFrame(data)
        expected_df_dict[f"df_{ticker}"] = df

    return expected_df_dict


def test_generate_dataframes():
    ipo_list = ["DBX", "SMAR", "CBLK", "EQH", "SPOT"]
    expected_df_dict = _create_expected_df_dict(ipo_list)

    temp_folder = _create_test_files()

    try:
        actual_df_dict = generate_dataframes(temp_folder, ipo_list)

        for df_name, expected_df in expected_df_dict.items():
            assert df_name in actual_df_dict, f"{df_name} not found in actual_df_dict"
            actual_df = actual_df_dict[df_name].reset_index(drop=True)

            for index, row in expected_df.iterrows():
                company_name = row["title"]
                actual_title = actual_df.loc[index, "title"]

                assert (
                    company_name in actual_title
                ), f"Company name '{company_name}' not found in actual title '{actual_title}'"

    finally:
        _delete_test_files(temp_folder)


date_string = "2018-01-01T00:00:00Z"
date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ").date()
formatted_date = date_obj.strftime("%Y-%m-%d")


def _create_expected_ipo_data_clean_with_date_objects():
    data = {
        "ticker": ["DBX", "SMAR", "CBLK", "EQH", "SPOT"],
        "trade_date": [
            "2018-03-23",
            "2018-04-27",
            "2018-05-04",
            "2018-05-10",
            "2018-04-03",
        ],
    }
    df = pd.DataFrame(data)
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
    return df


def _create_test_df(company_name):
    data = {
        "title": [f"{company_name} announces their IPO"],
        "published": [formatted_date],
    }
    return pd.DataFrame(data)


def test_filter_df_by_ipo_date():
    test_df_dict = {
        f"df_{company_name}": _create_test_df(company_name)
        for ticker, company_name in {
            "DBX": "Dropbox",
            "SMAR": "Smartsheet",
            "CBLK": "Carbon Black",
            "EQH": "AXA",
            "SPOT": "Spotify",
        }.items()
    }
    for ticker, company_name in {
        "DBX": "Dropbox",
        "SMAR": "Smartsheet",
        "CBLK": "Carbon Black",
        "EQH": "AXA",
        "SPOT": "Spotify",
    }.items():
        filtered_df = filter_df_by_ipo_date(test_df_dict, company_name, ticker)

        for _index, row in filtered_df.iterrows():
            company_in_title = company_name in row["title"]
            assert company_in_title, f"Expected {company_name} in title, but not found"

            published_date = row["published"]
            ipo_date = (
                _create_expected_ipo_data_clean_with_date_objects()
                .loc[
                    _create_expected_ipo_data_clean_with_date_objects()["ticker"]
                    == ticker,
                    "trade_date",
                ]
                .values[0]
            )

            assert (
                published_date < ipo_date
            ), f"Expected published date {published_date} to be before IPO date {ipo_date}"


def _create_expected_ipo_data_clean_with_company_names():
    data = {
        "ticker": ["DBX", "SMAR", "CBLK", "EQH", "SPOT"],
        "company_name": ["Dropbox", "Smartsheet", "Carbon Black", "AXA", "Spotify"],
        "trade_date": [
            "2018-03-23",
            "2018-04-27",
            "2018-05-04",
            "2018-05-10",
            "2018-04-03",
        ],
    }
    ipo_info = pd.DataFrame(data)
    ipo_info["trade_date"] = pd.to_datetime(ipo_info["trade_date"]).dt.date
    ipo_info = ipo_info.set_index("ticker")
    return ipo_info


def test_filter_and_store_df_by_ipo_date():
    ipo_info = _create_expected_ipo_data_clean_with_company_names()
    test_df_dict = {
        f"df_{company_name}": _create_test_df(company_name)
        for _, company_name in {
            "DBX": "Dropbox",
            "SMAR": "Smartsheet",
            "CBLK": "Carbon Black",
            "EQH": "AXA",
            "SPOT": "Spotify",
        }.items()
    }

    filtered_dfs = filter_and_store_df_by_ipo_date(ipo_info, test_df_dict)

    for ticker, company_name in {
        "DBX": "Dropbox",
        "SMAR": "Smartsheet",
        "CBLK": "Carbon Black",
        "EQH": "AXA",
        "SPOT": "Spotify",
    }.items():
        filtered_df = filtered_dfs[f"df_{ticker}"]

        for _index, row in filtered_df.iterrows():
            company_in_title = company_name in row["title"]
            assert company_in_title, f"Expected {company_name} in title, but not found"

            published_date = row["published"]
            ipo_date = ipo_info.loc[ticker, "trade_date"]

            assert (
                published_date < ipo_date
            ), f"Expected published date {published_date} to be before IPO date {ipo_date}"


def test_split_text():
    expected_words_df = pd.DataFrame(
        {"words": ["IPO", "underpricing", "test", "sentence"]},
    )
    df = pd.DataFrame({"text": ["IPO underpricing test sentence"]})
    ticker = "TEST"
    words_df = split_text(df, ticker)

    assert_frame_equal(expected_words_df, words_df)
