"""
data_ingestion.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Day 1: Load all 10 provided CSV datasets, inspect shape/dtypes/head, and flag anomalies.
"""

import pandas as pd
from pathlib import Path

# Use pathlib so this works on any OS (Windows/Mac/Linux) - avoids hardcoded paths (a common mistake flagged in the project doc)
RAW_DATA_DIR = Path("data/raw")

# Dictionary mapping a short, easy-to-use name -> actual filename on disk
DATASET_FILES = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv",
}


def load_all_datasets():
    """
    Loads all 10 CSV files into a dictionary of DataFrames.
    Returns: dict of {dataset_name: DataFrame}
    """
    dataframes = {}

    for name, filename in DATASET_FILES.items():
        file_path = RAW_DATA_DIR / filename
        try:
            df = pd.read_csv(file_path)
            dataframes[name] = df
            print(f"Loaded '{name}' successfully from {filename}")
        except FileNotFoundError:
            print(f"!! FILE NOT FOUND: {file_path} -- check the filename/location.")
        except Exception as e:
            print(f"!! ERROR loading '{name}': {e}")

    return dataframes


def inspect_dataset(name, df):
    """
    Prints shape, dtypes, and head for a single DataFrame,
    plus a basic anomaly check (nulls, duplicate rows).
    """
    print("\n" + "=" * 70)
    print(f"DATASET: {name}")
    print("=" * 70)

    print(f"\nShape (rows, columns): {df.shape}")

    print("\nColumn data types:")
    print(df.dtypes)

    print("\nFirst 5 rows:")
    print(df.head())

    # Basic anomaly checks
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    duplicate_rows = df.duplicated().sum()

    print(f"\nTotal missing values: {total_nulls}")
    if total_nulls > 0:
        print("Columns with missing values:")
        print(null_counts[null_counts > 0])

    print(f"Duplicate rows: {duplicate_rows}")


def main():
    print("Starting data ingestion for Bluestock MF Capstone...\n")

    dataframes = load_all_datasets()

    print(f"\n{len(dataframes)} out of {len(DATASET_FILES)} datasets loaded successfully.\n")

    for name, df in dataframes.items():
        inspect_dataset(name, df)

    print("\nData ingestion complete.")


if __name__ == "__main__":
    main()