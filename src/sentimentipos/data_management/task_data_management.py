import pandas as pd
import pytask

from sentimentipos.config import BLD, SRC
from sentimentipos.data_management import (
    filter_and_store_df_by_ipo_date,
    generate_dataframes,
    get_ipo_data_clean,
    get_ipo_info,
    ipo_tickers,
    split_text,
    unzipper,
)


# Task 1
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
    """Unzips archive.zip, stores files in 'unzipped' folder within data folder in BLD."""
    unzipper(depends_on["json_zip"], produces["unzipped"])
    folder_names = ["figures", "models", "tables"]
    for folder_name in folder_names:
        folder_path = produces["bld_python_path"] / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)


# Task 2
@pytask.mark.depends_on(
    {
        # "unzipped_json_files": BLD / "python" / "data" / "unzipped", ### could try removing this dependency
        "orginal_data": SRC
        / "data"
        / "original_ipo_data.xlsx",
    },
)
@pytask.mark.produces(
    {
        "ipo_data_clean": BLD / "python" / "data" / "ipo_data_clean.xlsx",
    },
)
def task_clean_data_excel(depends_on, produces):
    """Reads IPO data, cleans, keeps essential rows/cols, saves as ipo_data_clean in BLD."""
    ipo_data_clean = get_ipo_data_clean(depends_on["orginal_data"])
    ipo_data_clean.to_excel(produces["ipo_data_clean"], index=False)


# Task 3
@pytask.mark.depends_on(
    {
        "unzipped_json_files": BLD / "python" / "data" / "unzipped",
        "excel_path": BLD / "python" / "data" / "ipo_data_clean.xlsx",
    },
)
@pytask.mark.produces(
    {
        "output_folder_path": BLD / "python" / "data",
        "tokenized": BLD / "python" / "data" / "tokenized_texts",
    },
)
def task_generate_ipo_data_and_dataframes(depends_on, produces):
    """Cleans Excel, unzips files, makes dataframes, tokenizes articles pre-IPO."""
    ipo_list = ipo_tickers()
    ipo_info = get_ipo_info(ipo_list)
    ipo_info = pd.DataFrame.from_dict(ipo_info, orient="index")
    ipo_info["ipo_date"] = pd.to_datetime(
        ipo_info["ipo_date"],
        errors="coerce",
        utc=True,
    ).dt.date
    ipo_info.to_csv(produces["output_folder_path"] / "ipo_info.csv", index=False)
    df_dict = generate_dataframes(
        depends_on["unzipped_json_files"],
        ipo_list,
    )
    df_dict = {
        f"df_{ipo_info.loc[ticker, 'company_name']}": df
        for ticker, df in zip(ipo_list, df_dict.values())
    }
    dfs_filtered = filter_and_store_df_by_ipo_date(ipo_info, df_dict)
    dfs_filtered = [(dfs_filtered[f"df_{ticker}"], ticker) for ticker in ipo_list]
    tokenized_texts_path = produces["tokenized"]
    tokenized_texts_path.mkdir(parents=True, exist_ok=True)

    for df, ticker in dfs_filtered:
        split_text(df, ticker)
