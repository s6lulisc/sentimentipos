import numpy as np
import pandas as pd


def get_ipo_df(file_path):
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
    ipo_df = ipo[mask]

    new_row = {
        "trade_date": "2018-04-03",
        "company": "Spotify",
        "ticker": "SPOT",
        "offr_price": 132,
        "open_price": 165.90,
        "1st_day_close": 149.01,
        "offr_prc_pct_rtrn": 12.89,
    }

    new_index = ipo_df.index.max() + 1
    ipo_df.loc[new_index] = new_row

    ipo_df["trade_date"] = pd.to_datetime(ipo_df["trade_date"], errors="coerce")
    ipo_df["trade_date"] = ipo_df["trade_date"].dt.strftime("%Y-%m-%d")

    def calculate_and_round(row):
        try:
            result = (row["1st_day_close"] - row["open_price"]) / row["open_price"]
            return round(result, 3)
        except (TypeError, ZeroDivisionError):
            return np.nan

    ipo_df["open_prc_pct_rtrn"] = ipo_df.apply(calculate_and_round, axis=1)

    ipo_df["company"] = ipo_df["company"].str.strip()
    ipo_df["company"].replace("AXA Equitable Holdings", "AXA", inplace=True)

    return ipo_df
