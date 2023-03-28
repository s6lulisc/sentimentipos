import os

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
    unzipper,
)


# Task #1. This task is unzipping the json files and storing them in the SRC / "data" / "unzipped" folder
@pytask.mark.depends_on(
    {
        "json_zip": SRC / "data" / "archive.zip",
    },
)
@pytask.mark.produces(
    {
        "unzipped": BLD / "python" / "data" / "unzipped",
        "bld_python_path": BLD / "python",
    },
)
@pytask.mark.try_first
def task_unzipper(depends_on, produces):
    unzipper(depends_on["json_zip"], produces["unzipped"])
    folder_names = ["figures", "models", "tables"]
    for folder_name in folder_names:
        folder_path = os.path.join(produces["bld_python_path"], folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        else:
            pass


# Task #2. This task generates and saves IPO data and dataframes.
@pytask.mark.depends_on(
    {
        "unzipped_json_files": BLD / "python" / "data" / "unzipped",
        "orginal_data": SRC / "data" / "original_ipo_data.xlsx",
    },
)
@pytask.mark.produces(
    {
        "ipo_df": BLD / "python" / "data" / "ipo_df.xlsx",
    },
)
def task_clean_data_excel(depends_on, produces):
    ipo_df = get_ipo_df(depends_on["orginal_data"])
    ipo_df.to_excel(produces["ipo_df"], index=False)


# Task #3. This task generates and saves IPO data and dataframes.
@pytask.mark.depends_on(
    {
        "unzipped_json_files": BLD / "python" / "data" / "unzipped",
        "excel_path": BLD / "python" / "data" / "ipo_df.xlsx",  #
    },
)
@pytask.mark.produces(
    {
        "output_folder_path": BLD / "python" / "data",
        "tokenized": BLD / "python" / "data" / "tokenized_texts",
    },
)
def task_generate_ipo_data_and_dataframes(depends_on, produces):
    pd.read_excel(depends_on["excel_path"])
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
    df_dict = generate_dataframes(
        depends_on["unzipped_json_files"],
        ipo_list,
    )
    companies_and_tickers = [
        (ipo_info.get(ticker).get("company_name"), ticker) for ticker in ipo_info
    ]
    dfs_filtered = {}
    dfs_filtered = filter_and_store_df_by_ipo_date(companies_and_tickers, df_dict)
    dfs_filtered = [(dfs_filtered[f"df_{ticker}"], ticker) for ticker in ipo_list]
    tokenized_texts_path = produces["tokenized"]
    os.makedirs(tokenized_texts_path, exist_ok=True)

    for df, ticker in dfs_filtered:
        split_text(df, ticker)
