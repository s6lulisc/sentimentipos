import json
import string
from pathlib import Path

import pandas as pd


def ipo_tickers():
    """Defines the tickers of the companies that need to be analyzed. This function is used to
    choose the companies for which sentiment analysis will be performed. Inserting the ticker of the
    company in this list will add it to the companies that are analyzed.

    Returns:
        ipo_tickers(list): A list of tickers of companies that went public in 2018, chosen
        by who is performing the analysis.

    """
    ipo_tickers = ["CBLK", "SPOT"]  # , "EQH", "SMAR", "DBX"]
    return ipo_tickers


def open_excel(path):
    """Opens the cleaned excel file.

    Args:
        path(str): the path to the cleaned excel file.

    Returns:
        ipo_data_clean (pd.Dataframe): a Pandas dataframe containing
        the cleaned data for IPOs that occurred in 2018.

    """
    ipo_data_clean = pd.read_excel(path)
    return ipo_data_clean


def get_ipo_info(ipo_list, ipo_data_clean):
    """Creates a dictionary assigning the corresponding value to the name of each company, IPO date
    and first day returns.

    Args:
        ipo_list (list): the list of tickers of companies for which the information is to be retrieved.
        ipo_data_clean() #####

    Returns:
        ipo_info (pd.DataFrame): a pandas dataframe containing the name of the company, the IPO date
            and the first day returns of each company in the ipo_list.

    """
    ipo_info = {}
    for ticker in ipo_list:
        company_name = ipo_data_clean.loc[
            ipo_data_clean["ticker"] == ticker,
            "company",
        ].values[0]
        ipo_tickers = ipo_data_clean.loc[
            ipo_data_clean["ticker"] == ticker,
            "ticker",
        ].values[0]
        ipo_date = ipo_data_clean.loc[
            ipo_data_clean["ticker"] == ticker,
            "trade_date",
        ].values[0]
        returns = ipo_data_clean.loc[
            ipo_data_clean["ticker"] == ticker,
            "open_prc_pct_rtrn",
        ].values[0]
        ipo_info[ticker] = {
            "company_name": company_name,
            "ticker": ipo_tickers,
            "ipo_date": ipo_date,
            "returns": returns,
        }

    ipo_info = pd.DataFrame.from_dict(ipo_info, orient="index")
    return ipo_info


def contains_word(file_path, word):
    """Checks if a JSON file contains the word used as input. Specifically, it will look for the
    name of the company in the title section.

    Args:
        file_path (str): The path to the JSON file that is to be analyzed.
        word (str): The word that the function will look for in the title of the JSON (the name of the company).

    Returns:
        bool: Returns True if the name of the company is in the title, False otherwise. #####??

    """
    try:
        with open(file_path, encoding="latin-1") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False

    return word in data.get("title", "") or word in data.get("content", "")


def get_matching_files(folder_path, word):
    """Searches the folder and its subfolders for files that contain the input word in their 'title'
    field, returning a list of matching files. Specifically, it searches through the unzipped folder
    for files that contain the company name in the titles of articles. This is done in order to
    obtain all the files containing articles discussing the company under scrutiny.

    Args:
        folder_path (str): The path to the folder to search in.
        word (str): The word to search for in the 'title' field of the files.

    Returns:
        matching_files (list): A list of file paths that contain the specified word in their 'title' field.

    """
    matching_files = []
    folder = Path(folder_path)
    for file_path in folder.rglob("*"):
        if file_path.is_file() and contains_word(str(file_path), word):
            matching_files.append(str(file_path))
    return matching_files


def generate_dataframes(folder_path, ipo_info):
    """First, it creates an empty folder to store the dictionaries that will be creates in the
    function.

    Then, it uses the function get_matching files to find the articles
    with the desired word in the title. After creating an empty dictionary, it
    associates to each element a pandas dataframe created with a for loop containing all
    the articles with the desired word in the title. The Dataframe is then stored in the
    empty folder created at the beginning of the function. Therefore, the function will
    create a dictionary assigning to each company a dataframe with the information
    contained in the JSON files that the function get_matching_files retrieves.

    Args:
        folder_path (str): The path to the folder to search through.
        ipo_info (pd.DataFrame): #####

    Returns:
        df_dict (dict): the dictionary associating to each dataframe name (df_<company_name>) the respective dataframe.

    """
    df_dict = {}
    for ticker, row in ipo_info.iterrows():
        company_name = row["company_name"]
        word = company_name
        matching_files = get_matching_files(folder_path, word)

        output_dict = {}
        for file_path in matching_files:
            with open(file_path, encoding="latin-1") as f:
                data = json.load(f)
                output_dict[file_path] = data

        df_name = f"df_{ticker}"
        df = pd.DataFrame.from_dict(output_dict, orient="index")
        df_dict[df_name] = df

    return df_dict


def filter_df_by_ipo_date(df_dict, company_name, ticker, ipo_info):
    """After retrieving the list of IPOs and the dataframe containing their information, it uses the
    date of the IPO to filter the dataframe containing the articles so that the new dataframe only
    contains the articles that were written before the IPO date. This is done because the analysis
    will only include the sentiment previous to the IPO, to see if there is a correlation between
    the sentiment and the IPO performance.

    Args:
        df_dict (dict): A dictionary of Pandas DataFrames containing article data for various companies.
        company (str): The name of the company to filter for.
        ticker (str): The stock ticker symbol of the company.
        ipo_info (): #####

    Returns:
        df_filtered (pd.DataFrame): A filtered DataFrame containing only the articles
        for the specified company that were published before its IPO date.

    """
    ipo_info.index.name = "ticker"
    ipo_info["ipo_date"] = pd.to_datetime(
        ipo_info["ipo_date"],
        errors="coerce",
        utc=True,
    ).dt.date
    df_company_name = df_dict[f"df_{company_name}"]
    df_company_name["published"] = pd.to_datetime(
        df_company_name.get("published"),
        errors="coerce",
        utc=True,
    )
    df_company_name["published"] = df_company_name["published"].dt.date
    ipo_date = ipo_info.loc[ticker, "ipo_date"]
    df_filtered = df_company_name[df_company_name["published"] < ipo_date]
    return df_filtered


def filter_and_store_df_by_ipo_date(ipo_info, df_dict):
    """After creating an empty dictionary, it fills it with a for loop associating to each element
    the corresponding dataframe filtered by IPO date.

    Args:
        ipo_info (pd.Dataframe): A dataframe containing the name of the companies, the
            day of their IPOs and their first day returns.
        df_dict (dict): A dictionary of data frames, where the keys are the names
            of the data frames and the values are the data frames themselves.

    Returns:
        dfs_filtered (dict): A dictionary of filtered data frames, where the keys are the
        names of the filtered data frames (which are in the format "df_<ticker>"), and the
        values are the corresponding data frames.

    """
    dfs_filtered = {}
    for ticker, row in ipo_info.iterrows():
        company_name = row["company_name"]
        filtered_df = filter_df_by_ipo_date(df_dict, company_name, ticker, ipo_info)
        df_name = f"df_{ticker}"
        dfs_filtered[df_name] = filtered_df
    return dfs_filtered


def split_text(
    df,
):  # got rid of argyment: ticker. ticker (str): The ticker symbol of the company corresponding to the DataFrame.
    """Extracts the text from the 'text' column of the specified DataFrame and splits it into
    individual words (tokenization), which are saved to a CSV file in a new folder with the
    specified `ticker` as the filename.

    Args:
        df (pd.DataFrame): The DataFrame to extract the text data from.

    Returns:
        words_df (pd.DataFrame): A DataFrame containing the individual words
        extracted from the text data, with a single column named 'words'.

    """
    text_col_name = "text"
    text_col = df[text_col_name]
    all_text = []
    for _index, row in text_col.iteritems():
        all_text.append(row)
    punctuation = string.punctuation.replace("-", "")
    only_text = [
        text.translate(str.maketrans("", "", punctuation)) for text in all_text
    ]
    ticker_text_str = ",".join(only_text)
    words = ticker_text_str.split()
    words_df = pd.DataFrame(words, columns=["words"])
    return words_df
