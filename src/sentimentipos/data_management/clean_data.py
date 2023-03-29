import numpy as np
import pandas as pd
import zipfile
import pathlib as Path
import shutil

import os

def unzipper(zip_path, out_path):
    """Unzips the file used as one of the arguments and moves it to a specific
    directory.

    Args:
        zip_path (str): The path to the zipped file that needs to be unzipped.
        out_path (str): The path to the directory where the unzipped file is stored.

    """
    with zipfile.ZipFile(zip_path) as zip_ref:
        zip_ref.extractall(out_path)


def get_ipo_data_clean(file_path):
    """
    Reads IPO data from an Excel file, filters and processes it to create a DataFrame with relevant IPO information.

    Parameters
    ----------
    file_path : str
        The path to the Excel file containing the raw IPO data.

    Returns
    -------
    get_ipo_data_clean : pd.DataFrame
        A DataFrame containing the processed IPO data with the following columns:
            - trade_date: The date when the IPO was traded.
            - company: The name of the company that went public.
            - ticker: The ticker symbol of the company.
            - offr_price: The offering price of the IPO.
            - open_price: The opening price of the IPO.
            - 1st_day_close: The closing price of the IPO on the first day of trading.
            - open_prc_pct_rtrn: The percentage return from the opening price to the first day close.

    """
    ipo = pd.read_excel(file_path)
    rows_to_drop = list(range(0, 37))
    ipo = ipo.drop(rows_to_drop)
    column_mapping = {
        "Unnamed: 0": "trade_date",
        "Unnamed: 1": "company",
        "Unnamed: 2": "ticker",
        "IPO SCOOP Rating Scorecard": "lead_jlead_mangr",
        "Unnamed: 4": "offr_price",
        "Unnamed: 5": "open_price",
        "Unnamed: 6": "1st_day_close",
        "Unnamed: 7": "offr_prc_pct_rtrn",
        "Unnamed: 8": "$_chg_open",
        "Unnamed: 9": "$_chg_close",
        "Unnamed: 10": "star_ratn",
        "Unnamed: 11": "del",
    }

    ipo = ipo.rename(columns=column_mapping)
    ipo["trade_date"] = ipo["trade_date"].astype(str)
    ipo["trade_date"] = pd.to_datetime(ipo["trade_date"], errors="coerce").dt.strftime(
        "%Y-%m-%d",
    )

    columns_to_drop = [
        "lead_jlead_mangr",
        "offr_prc_pct_rtrn",
        "$_chg_open",
        "$_chg_close",
        "star_ratn",
        "del",
    ]

    # Check if the columns exist in the DataFrame before dropping them
    columns_to_drop = [col for col in columns_to_drop if col in ipo.columns]

    ipo = ipo.drop(columns=columns_to_drop, axis=1)

    ipo["trade_date"] = pd.to_datetime(ipo["trade_date"], errors="coerce")
    start_date = "2018-01-01"
    end_date = "2018-06-30"

    mask = (ipo["trade_date"] >= start_date) & (ipo["trade_date"] <= end_date)
    ipo_data_clean = ipo[mask]

    new_row = {
        "trade_date": "2018-04-03",
        "company": "Spotify",
        "ticker": "SPOT",
        "offr_price": 132,
        "open_price": 165.90,
        "1st_day_close": 149.01,
        "offr_prc_pct_rtrn": 12.89,
    }

    new_index = ipo_data_clean.index.max() + 1
    ipo_data_clean.loc[new_index] = new_row

    ipo_data_clean["trade_date"] = pd.to_datetime(ipo_data_clean["trade_date"], errors="coerce")
    ipo_data_clean["trade_date"] = ipo_data_clean["trade_date"].dt.strftime("%Y-%m-%d")

    def calculate_and_round(row):
        try:
            result = (row["1st_day_close"] - row["open_price"]) / row["open_price"]
            return round(result, 3)
        except (TypeError, ZeroDivisionError):
            return np.nan

    ipo_data_clean["open_prc_pct_rtrn"] = ipo_data_clean.apply(calculate_and_round, axis=1)

    ipo_data_clean["company"] = ipo_data_clean["company"].str.strip()
    ipo_data_clean["company"].replace("AXA Equitable Holdings", "AXA", inplace=True)

    return ipo_data_clean
