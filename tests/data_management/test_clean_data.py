import json
import os
import zipfile
from pathlib import Path

import pandas as pd
import pytest
from sentimentipos.config import SRC
from sentimentipos.data_management.clean_data import (
    contains_word,
    generate_dataframes,
    get_company_name,
    get_ipo_date,
    get_ipo_df,
    get_matching_files,
    get_returns,
    unzipper,
    transpose_all_dataframes,
    filter_df_by_ipo_date
)


def test_unzipper(tmpdir):
    # Create a temporary zip file with a text file inside
    zip_file_path = tmpdir.join("test.zip")
    text_file_path = tmpdir.join("test.txt")

    with open(text_file_path, "w") as f:
        f.write("IPO underpricing")

    with zipfile.ZipFile(zip_file_path, "w") as zf:
        zf.write(text_file_path, "test.txt")

    # Call unzipper to extract the contents of the zip file
    unzipper(zip_file_path, tmpdir)

    # Check if the text file was extracted correctly
    extracted_file_path = tmpdir.join("test.txt")
    assert os.path.exists(extracted_file_path)

    with open(extracted_file_path) as f:
        content = f.read()

    assert content == "IPO underpricing"


@pytest.fixture(scope="module")
def ipo_df_path():
    path = Path(SRC / "data/ipo_df.xlsx")
    return path


def test_get_ipo_df(ipo_df_path):
    ipo_df = get_ipo_df(ipo_df_path)

    assert isinstance(ipo_df, pd.DataFrame)
    assert not ipo_df.empty
    assert set(ipo_df.columns) == {
        "trade_date",
        "issuer",
        "symbol",
        "lead_jlead_mangr",
        "offr_price",
        "open_price",
        "1st_d_close",
        "1st_d_%_chg",
        "%_chg_open",
        "$_chg_close",
        "star_ratn",
        "open_prc_pct_rtrn",
    }


# Test data
test_data = [
    ("DBX", "Dropbox", "2018-03-23"),
    ("SPOT", "Spotify", "2018-04-03"),
    ("EQH", "AXA", "2018-05-10"),
]


@pytest.mark.parametrize(
    ("ticker", "expected_company_name", "expected_ipo_date"),
    test_data,
)
def test_get_company_name(
    ipo_df_path,
    ticker,
    expected_company_name,
    expected_ipo_date,
):
    company_name, _ = get_company_name(ticker)
    assert company_name == expected_company_name


@pytest.mark.parametrize(("ticker", "_", "expected_ipo_date"), test_data)
def test_get_ipo_date(ipo_df_path, ticker, _, expected_ipo_date):
    ipo_date, _ = get_ipo_date(ticker)
    assert str(ipo_date)[:10] == expected_ipo_date


@pytest.mark.parametrize(
    ("ticker", "expected_return"),
    [
        ("DBX", -0.017931034482758606),
        ("SPOT", -0.10180831826401456),
        ("EQH", 0.02987341772151898),
    ],
)
def test_get_returns(ipo_df_path, ticker, expected_return):
    returns, _ = get_returns(ticker)
    assert returns == expected_return


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
    # Create JSON files with and without the target word
    target_word = "IPO"
    file_contents = [
        {"title": "IPO is in the title", "content": "Random content"},
        {"title": "Title without the target word", "content": "Random content"},
        {"title": "Another title with target_word IPO", "content": "Random content"},
    ]

    for i, content in enumerate(file_contents):
        file_path = tmpdir.join(f"file_{i}.json")
        with open(file_path, "w") as f:
            json.dump(content, f)

    # Call get_matching_files and check the result
    matching_files = get_matching_files(tmpdir, target_word)

    # Check if the number of matching files is as expected
    assert len(matching_files) == 2

    # Check if the matching files contain the target word
    for file_path in matching_files:
        with open(file_path) as f:
            data = json.load(f)
        assert target_word in data["title"]


def test_generate_dataframes(tmpdir):
    # Create JSON files with desired words
    desired_words = ["IPO", "Acquisition"]
    file_contents = [
        {"title": "IPO is in the title", "content": "Random content"},
        {"title": "Title without the desired words", "content": "Random content"},
        {"title": "Another title with target_word IPO", "content": "Random content"},
        {"title": "Acquisition is in the title", "content": "Random content"},
    ]

    folder_path = tmpdir.mkdir("input_files")
    for i, content in enumerate(file_contents):
        file_path = folder_path.join(f"file_{i}.json")
        with open(file_path, "w") as f:
            json.dump(content, f)

    # Create a temporary output folder
    output_folder_path = tmpdir.mkdir("output_files")

    # Call generate_dataframes and check the result
    df_dict = generate_dataframes(folder_path, desired_words, output_folder_path)

    # Check if the generated DataFrames match the expected structure and content
    for word in desired_words:
        df_name = f'df_{word.replace(" ", "")}'
        assert df_name in df_dict
        df = df_dict[df_name]
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    # Check if the matching JSON files were created in the output folder
    matching_json_folder_path = os.path.join(output_folder_path, "matching_json_files")
    for word in desired_words:
        output_file_name = f"matching_files_{word}.json"
        output_file_path = os.path.join(matching_json_folder_path, output_file_name)
        assert os.path.exists(output_file_path)

######################################

@pytest.mark.parametrize("df_dict", [
    {'df1': pd.DataFrame({'A': [1, 2], 'B': [3, 4]}),
     'df2': pd.DataFrame({'C': [5, 6], 'D': [7, 8]})},
    {'df1': pd.DataFrame({'A': [1], 'B': [2]}),
     'df2': pd.DataFrame({'C': [3], 'D': [4]})},
])
def test_transpose_all_dataframes(df_dict):
    expected_dict = {}
    for name, df in df_dict.items():
        expected_dict[name] = df.T

    actual_dict = transpose_all_dataframes(df_dict)

    for name, df in actual_dict.items():
        assert df.equals(expected_dict[name])




#@pytest.fixture
#def example_data():
#    # Define example data
#    df_dict = {
#        "df_company": pd.DataFrame({
#            "published": ["2021-01-01", "2021-02-01", "2022-01-01"],
#            "headline": ["Article 1", "Article 2", "Article 3"]
#        })
#    }
#    company = "company"
#    ticker = "AAPL"
#    
#    return df_dict, company, ticker
#
#def test_filter_df_by_ipo_date(example_data):
#    # Unpack example data
#    df_dict, company, ticker = example_data
#    
#    # Call function to be tested
#    result_df = filter_df_by_ipo_date(df_dict, company, ticker)
#    
#    # Define expected output
#    expected_df = pd.DataFrame({
#        "published": ["2021-01-01", "2021-02-01"],
#        "headline": ["Article 1", "Article 2"]
#    })
#    
#    # Compare result to expected output
#    pd.testing.assert_frame_equal(result_df, expected_df)



