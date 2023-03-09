import pandas as pd
import pytask

from sentimentipos.config import BLD, SRC
from sentimentipos.data_management import (
    filter_and_store_df_by_ipo_date,
    generate_dataframes,
    get_ipo_df,
    get_ipo_info,
    ipo_tickers,
    split_text,
    transpose_all_dataframes,
    unzipper,
)


# Task #1. This task is unzipping the json files and storing them in the SRC / "data" / "unzipped" folder
@pytask.mark.depends_on(
    {
        "scripts": SRC / "data_management" / "clean_data.py",
        "json_zip": SRC / "data" / "archive.zip",
    },
)
@pytask.mark.produces(BLD / "python" / "data" / "unzipped")
@pytask.mark.try_first
def task_unzipper(depends_on, produces):
    unzipper(depends_on["json_zip"], produces)


# Task #2. This task does the remainng data managemennt and stores matching json files of the companies of interest as well as tokenized csv files of the text column from the articles.
@pytask.mark.depends_on(
    {
        "scripts": SRC / "data_management" / "clean_data.py",
        "json_zip": SRC / "data" / "archive.zip",
        "ipo_df": SRC / "data" / "ipo_df.xlsx",
        "unzipped_json_files": SRC / "data",
    },
)
@pytask.mark.produces(
    {
        "output_folder_path": BLD / "python" / "data",
    },
)
@pytask.mark.try_last
def task_df_dict(depends_on, produces):
    get_ipo_df(depends_on["ipo_df"])
    ipo_list = ipo_tickers()
    ipo_info = get_ipo_info(ipo_list)
    df_info = pd.DataFrame.from_dict(ipo_info, orient="index")
    df_info.index.name = "ticker"
    df_info["ipo_date"] = pd.to_datetime(
        df_info["ipo_date"],
        errors="coerce",
        utc=True,
    ).dt.date
    df_info.to_csv(produces["output_folder_path"] / "df_info.csv", index=False)
    desired_words = list(df_info["company_name"])
    df_dict = {}
    df_dict = generate_dataframes(
        produces["output_folder_path"] / "unzipped",
        desired_words,
        produces["output_folder_path"],
    )
    transpose_all_dataframes(df_dict)
    companies_and_tickers = [
        (ipo_info.get(ticker).get("company_name"), ticker) for ticker in ipo_info
    ]
    dfs_filtered = {}
    # for df, ticker in df_and_tickers:
    dfs_filtered = filter_and_store_df_by_ipo_date(companies_and_tickers, df_dict)
    dfs_filtered = [(dfs_filtered[f"df_{ticker}"], ticker) for ticker in ipo_list]
    for df, ticker in dfs_filtered:
        split_text(df, ticker)
