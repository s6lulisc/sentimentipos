import json
import os
import string
import zipfile

import pandas as pd


def unzipper(zip_path, out_path):
    """Unzips the file used as one of the arguments and moves it to a specific
    directory.

    Args:
        zip_path (str): The path to the zipped file that needs to be unzipped.
        out_path (str): The path to the directory where the unzipped file is stored.

    """
    with zipfile.ZipFile(zip_path) as zip_ref:
        zip_ref.extractall(out_path)


def get_ipo_df(path):
    """Reads the excel file in the specified path. In this case it is a dataframe
    containing information about IPOs that happened in 2018.

    Args:
        path (str): The path to the excel file that needs to be read.

    Returns:
        ipo_df (pd.Dataframe): A pandas dataframe containing information regarding IPOs.

    """
    ipo_df = pd.read_excel(path)
    return ipo_df


def ipo_tickers():
    """Defines the tickers of the companies that need to be analyzed. This function is
    used to choose the companies for which sentiment analysis will be performed.
    Inserting the ticker of the company in this list will add it to the companies that
    are analyzed.

    Returns:
        ipo_tickers(list): A list of tickers of companies that went public in 2018, chosen
        by who is performing the analysis.

    """
    ipo_tickers = ["DBX", "SPOT", "EQH", "SMAR", "WHD"]
    return ipo_tickers


def get_company_name(ticker):
    """Stores the name of the company whose ticker we use as input in a variable called
    company_name. This function uses the function get_ipo_df to read the excel file
    containing the necessary information.

    Args:
        ticker (str): The ticker of the company whose name is to be retrieved.

    Returns:
        company_name (str): The name of the company associated with the ticker used as input.

    """
    ipo_df = get_ipo_df("src/sentimentipos/data/ipo_df.xlsx")
    company_name = ipo_df.loc[ipo_df["symbol"] == ticker, "issuer"].values[0]
    return company_name, print(company_name)


def get_ipo_date(ticker):
    """Stores the IPO date of the company whose ticker we use as input in a variable
    called ipo_date. This function uses the function get_ipo_df to read the excel file
    containing the necessary information.

    Args:
        ticker (str): The ticker of the company whose IPO date is to be retrieved.

    Returns:
        ipo_date (pd.DateTime): The IPO date of the company associated with the ticker used as input.

    """
    ipo_df = pd.read_excel("src/sentimentipos/data/ipo_df.xlsx")
    ipo_date = ipo_df.loc[ipo_df["symbol"] == ticker, "trade_date"].values[0]
    return ipo_date, print(ipo_date)


def get_returns(ticker):
    """Stores the first day returns of the company whose ticker we use as input in a
    variable called returns. This function uses the function get_ipo_df to read the
    excel file containing the necessary information.

    Args:
        ticker (str): The ticker of the company whose IPO date is to be retrieved.

    Returns:
        returns (float): The first day returns of the company associated with the
            ticker used as input.

    """
    ipo_df = pd.read_excel("src/sentimentipos/data/ipo_df.xlsx")
    returns = ipo_df.loc[ipo_df["symbol"] == ticker, "open_prc_pct_rtrn"].values[0]
    return returns, print(returns)


def get_ipo_info(ipo_list):
    """Creates a dictionary assigning the corresponding value to the name of each
    company, IPO date and first day returns. This function uses the functions
    get_company_name, get_ipo_date and get_returns to retrieve the necessary
    information.

    Args:
        ipo_list (list): the list of tickers of companies for which the information is to be retrieved.

    Returns:
        ipo_info (dict): a dictionary containing the name of the company, the IPO date
            and the first day returns of each company in the ipo_list.

    """
    ipo_info = {}
    for ticker in ipo_list:
        company_name = get_company_name(ticker)[0]
        ipo_date = get_ipo_date(ticker)[0]
        returns = get_returns(ticker)[0]
        ipo_info[ticker] = {
            "company_name": company_name,
            "ipo_date": ipo_date,
            "returns": returns,
        }
    return ipo_info


def contains_word(file_path, word):
    """Checks if a JSON file contains the word used as input. Specifically, it will look
    for the name of the company in the title section.

    Args:
        file_path (str): The path to the JSON file that is to be analyzed.
        word (str): The word that the function will look for in the title of the JSON (the name of the company).

    Returns:
        bool: Returns True if the name of the company is in the title, False otherwise.

    """
    try:
        with open(file_path, encoding="latin-1") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False

    return word in data.get("title", "") or word in data.get("content", "")


def get_matching_files(folder_path, word):
    """Searches the folder and its subfolders for files that contain the input word in
    their 'title' field, returning a list of matching files. Specifically, it searches
    through the unzipped folder for files that contain the company name in the titles of
    articles. This is done in order to obtain all the files containing articles
    discussing the company under scrutiny.

    Args:
        folder_path (str): The path to the folder to search in.
        word (str): The word to search for in the 'title' field of the files.

    Returns:
        matching_files (list): A list of file paths that contain the specified word in their 'title' field.

    """
    matching_files = []
    for dirpath, _dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if contains_word(file_path, word):
                matching_files.append(file_path)
    return matching_files


def generate_dataframes(folder_path, desired_words, output_folder_path):
    """First, it reates an empty folder to store the dictionaries that will be creates
    in the function. Then, it uses the function get_matching files to find the articles
    with the desired word in the title. After creating an empty dictionary, it
    associates to each element a pandas dataframe created with a for loop containing all
    the articles with the desired word in the title. The Dataframe is then stored in the
    empty folder created at the beginning of the function. Therefore, the function will
    create a dictionary assigning to each company a dataframe with the information
    contained in the JSON files that the function get_matching_files retrieves.

    Args:
        folder_path (str): The path to the folder to search through.
        desired_words (list): A list of words to search for in the 'title' field of the JSON files.
        output_folder_path (str): The path to the folder where the generated DataFrames will be saved.

    Returns:
        df_dict (dict): the dictionary associating to each dataframe name (df_<company_name>) the respective dataframe.

    """
    # Create the output folder if it does not exist
    matching_json_folder_path = os.path.join(output_folder_path, "matching_json_files")
    if not os.path.exists(matching_json_folder_path):
        os.makedirs(matching_json_folder_path)

    df_dict = {}
    for word in desired_words:
        matching_files = get_matching_files(folder_path, word)
        output_dict = {}
        for file_path in matching_files:
            with open(file_path, encoding="latin-1") as f:
                data = json.load(f)
                output_dict[file_path] = data
        output_file_name = f"matching_files_{word}.json"
        output_file_path = os.path.join(matching_json_folder_path, output_file_name)
        with open(output_file_path, "w") as f:
            json.dump(output_dict, f)
        df_name = f'df_{word.replace(" ", "")}'
        df = pd.read_json(output_file_path)
        df_dict[df_name] = df
    return df_dict


def transpose_all_dataframes(df_dict):
    """Calls each element of the dictionary, transposes the associated pandas dataframe
    and stores the transposed the dataframe in the original dictionary.

    Args:
        df_dict (dict): A dictionary of Pandas DataFrames to be transposed.

    Returns:
        df_dict (dict): The same dictionary containing the transposed Pandas DataFrames.

    """
    for name, df in df_dict.items():
        df_dict[name] = df.T

    return df_dict


def filter_df_by_ipo_date(df_dict, company, ticker):
    """After retrieving the list of IPOs and the dataframe containing their information,
    it uses the date of the IPO to filter the dataframe containing the articles so that
    the new dataframe only contains the articles that were written before the IPO date.
    This is done because the analysis will only include the sentiment previous to the
    IPO, to see if there is a correlation between the sentiment and the IPO performance.

    Args:
        df_dict (dict): A dictionary of Pandas DataFrames containing article data for various companies.
        company (str): The name of the company to filter for.
        ticker (str): The stock ticker symbol of the company.

    Returns:
        df_filtered (pd.DataFrame): A filtered DataFrame containing only the articles
        for the specified company that were published before its IPO date.

    """
    ipo_list = ipo_tickers()
    ipo_info = get_ipo_info(ipo_list)
    df_info = pd.DataFrame.from_dict(ipo_info, orient="index")
    df_info.index.name = "ticker"
    df_info["ipo_date"] = pd.to_datetime(
        df_info["ipo_date"],
        errors="coerce",
        utc=True,
    ).dt.date
    global desired_words
    desired_words = list(df_info["company_name"])
    df_company = df_dict[f"df_{company}"]
    df_company["published"] = pd.to_datetime(
        df_company["published"],
        errors="coerce",
        utc=True,
    )
    df_company["published"] = df_company["published"].dt.date
    ipo_date = df_info.loc[ticker, "ipo_date"]
    df_filtered = df_company[df_company["published"] < ipo_date]
    return df_filtered


def filter_and_store_df_by_ipo_date(companies_and_tickers, df_dict):
    """After creating an empty dictionary, it fills it with a for loop associating to
    each element the corresponding dataframe filtered by IPO date.

    Args:
        companies_and_tickers (list of tuples): A list of tuples, where each tuple
            contains the name of a company and its corresponding ticker.
        df_dict (dict): A dictionary of data frames, where the keys are the names
            of the data frames and the values are the data frames themselves.

    Returns:
        dfs_filtered (dict): A dictionary of filtered data frames, where the keys are the
        names of the filtered data frames (which are in the format "df_<ticker>"), and the
        values are the corresponding data frames.

    """
    dfs_filtered = {}
    for company, ticker in companies_and_tickers:
        filtered_df = filter_df_by_ipo_date(df_dict, company, ticker)
        df_name = f"df_{ticker}"
        globals()[df_name] = filtered_df
        dfs_filtered[df_name] = filtered_df
    return dfs_filtered


def split_text(df, ticker):
    """Extracts the text from the 'text' column of the specified DataFrame and splits it
    into individual words (tokenization), which are saved to a CSV file in a new folder
    with the specified `ticker` as the filename.

    Args:
        df (pd.DataFrame): The DataFrame to extract the text data from.
        ticker (str): The ticker symbol of the company corresponding to the DataFrame.

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
    globals()[f"{ticker}_text"] = ticker_text_str
    words = ticker_text_str.split()
    globals()[f"{ticker}_words"] = words
    words_df = pd.DataFrame(words, columns=["words"])
    words_df.to_csv(f"bld/python/data/tokenized_texts/{ticker}.csv", index=False)
    return words_df
