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

def explore_fund_master(df):
    """
    Explores the fund_master dataset specifically:
    - unique fund houses, categories, sub-categories, risk grades
    - basic understanding of AMFI scheme code structure
    """
    print("\n" + "=" * 70)
    print("FUND MASTER — DETAILED EXPLORATION")
    print("=" * 70)

    print(f"\nTotal schemes: {len(df)}")

    print(f"\nUnique Fund Houses ({df['fund_house'].nunique()}):")
    print(df['fund_house'].unique())

    print(f"\nUnique Categories ({df['category'].nunique()}):")
    print(df['category'].unique())

    print(f"\nUnique Sub-Categories ({df['sub_category'].nunique()}):")
    print(df['sub_category'].unique())

    print(f"\nUnique Risk Categories ({df['risk_category'].nunique()}):")
    print(df['risk_category'].unique())

    print(f"\nUnique Plans:")
    print(df['plan'].unique())

    print(f"\nUnique SEBI Category Codes:")
    print(df['sebi_category_code'].unique())

    # AMFI scheme code structure - just look at the range and format
    print(f"\nAMFI Code (amfi_code) data type: {df['amfi_code'].dtype}")
    print(f"Sample AMFI codes: {df['amfi_code'].head(5).tolist()}")
    print(f"AMFI code range: {df['amfi_code'].min()} to {df['amfi_code'].max()}")

    # Fund house x category breakdown
    print("\nNumber of schemes per Fund House:")
    print(df['fund_house'].value_counts())

    print("\nNumber of schemes per Category:")
    print(df['category'].value_counts())
    
    
def validate_amfi_codes(fund_master_df, nav_history_df):
    """
    Checks that every amfi_code in fund_master also appears in nav_history.
    This confirms we have NAV history for every fund we know about,
    and flags any mismatch.
    """
    print("\n" + "=" * 70)
    print("AMFI CODE VALIDATION: fund_master vs nav_history")
    print("=" * 70)

    master_codes = set(fund_master_df['amfi_code'].unique())
    nav_codes = set(nav_history_df['amfi_code'].unique())

    print(f"\nUnique codes in fund_master: {len(master_codes)}")
    print(f"Unique codes in nav_history: {len(nav_codes)}")

    # Codes in fund_master but missing from nav_history (a real problem if non-empty)
    missing_from_nav = master_codes - nav_codes
    # Codes in nav_history but not in fund_master (extra/orphan data, worth knowing about)
    extra_in_nav = nav_codes - master_codes

    if missing_from_nav:
        print(f"\n!! WARNING: {len(missing_from_nav)} fund_master codes have NO nav_history data:")
        print(sorted(missing_from_nav))
    else:
        print("\nAll fund_master codes have corresponding nav_history data. PASS.")

    if extra_in_nav:
        print(f"\nNote: {len(extra_in_nav)} codes exist in nav_history but not in fund_master:")
        print(sorted(extra_in_nav))
    else:
        print("No extra/orphan codes in nav_history. PASS.")

    return missing_from_nav, extra_in_nav


def main():
    print("Starting data ingestion for Bluestock MF Capstone...\n")

    dataframes = load_all_datasets()

    print(f"\n{len(dataframes)} out of {len(DATASET_FILES)} datasets loaded successfully.\n")

    for name, df in dataframes.items():
        inspect_dataset(name, df)

    # Detailed exploration of fund_master specifically
    if "fund_master" in dataframes:
        explore_fund_master(dataframes["fund_master"])

    # Validate AMFI codes between fund_master and nav_history
    if "fund_master" in dataframes and "nav_history" in dataframes:
        validate_amfi_codes(dataframes["fund_master"], dataframes["nav_history"])

    print("\nData ingestion complete.")


if __name__ == "__main__":
    main()