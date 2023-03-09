# this is our part of the code

import json
import os
import random
import zipfile

import pandas as pd


def unzipper(zip_path, out_path):
    with zipfile.ZipFile(zip_path) as zip_ref:
        zip_ref.extractall(out_path)


def get_ipo_df(path):
    ipo_df = pd.read_excel(path)
    return ipo_df


def ipo_tickers():
    ipo_tickers = ["DBX", "SPOT", "EQH"]
    return ipo_tickers


def get_company_name(ticker):
    ipo_df = get_ipo_df("src/sentimentipos/data/ipo_df.xlsx")
    company_name = ipo_df.loc[ipo_df["symbol"] == ticker, "issuer"].values[0]
    return company_name, print(company_name)


def get_ipo_date(ticker):
    ipo_df = pd.read_excel("src/sentimentipos/data/ipo_df.xlsx")
    ipo_date = ipo_df.loc[ipo_df["symbol"] == ticker, "trade_date"].values[0]
    return ipo_date, print(ipo_date)


def get_returns(ticker):
    ipo_df = pd.read_excel("src/sentimentipos/data/ipo_df.xlsx")
    returns = ipo_df.loc[ipo_df["symbol"] == ticker, "open_prc_pct_rtrn"].values[0]
    return returns, print(returns)


def get_ipo_info(ipo_list):
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
    try:
        with open(file_path, encoding="latin-1") as f:
            data = json.load(f)
            # Check if the JSON data contains the word
            if "title" in data and word in data["title"]:
                return True
    except json.JSONDecodeError:
        return False


def get_matching_files(folder_path, word):
    matching_files = []
    for dirpath, _dirnames, filenames in os.walk(folder_path):
        random.shuffle(filenames)
        random_sample = filenames[: int(len(filenames) * 0.1)]
        for filename in random_sample:
            file_path = os.path.join(dirpath, filename)
            if contains_word(file_path, word):
                matching_files.append(file_path)
    return matching_files


def generate_dataframes(folder_path, desired_words, output_folder_path):
    df_dict = {}
    for word in desired_words:
        matching_files = get_matching_files(folder_path, word)
        output_dict = {}
        for file_path in matching_files:
            with open(file_path, encoding="latin-1") as f:
                data = json.load(f)
                output_dict[file_path] = data
        output_file_name = f"matching_files_{word}.json"
        output_file_path = os.path.join(output_folder_path, output_file_name)
        with open(output_file_path, "w") as f:
            json.dump(output_dict, f)
        df_name = f'df_{word.replace(" ", "")}'
        df = pd.read_json(output_file_path)
        df_dict[df_name] = df
    return df_dict


###############################################


def transpose_all_dataframes(df_dict):
    for name, df in df_dict.items():
        df_dict[name] = df.T

    return df_dict


def filter_df_by_ipo_date(df_dict, company, ticker):
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
    dfs_filtered = {}
    for company, ticker in companies_and_tickers:
        # filter data frame by IPO date
        filtered_df = filter_df_by_ipo_date(df_dict, company, ticker)
        # set the name of the filtered data frame
        df_name = f"df_{ticker}"
        # assign the filtered data frame to the variable with the given name
        globals()[df_name] = filtered_df
        # store the filtered data frame in the dictionary
        dfs_filtered[df_name] = filtered_df
    return dfs_filtered


def split_text(df, ticker):
    text_col_name = "text"
    text_col = df[text_col_name]  # get the 'text' column from the DataFrame
    all_text = []  # create an empty list to store the text values

    for _index, row in text_col.iteritems():
        all_text.append(row)  # add the text value from the current row to the list

    ticker_text_str = ",".join(all_text)
    globals()[f"{ticker}_text"] = ticker_text_str
    words = ticker_text_str.split()
    globals()[f"{ticker}_words"] = words

    words_df = pd.DataFrame(words, columns=["words"])

    # Save the DataFrame to a CSV file and return it
    words_df.to_csv(f"bld/python/data/{ticker}.csv", index=False)
    return words_df
