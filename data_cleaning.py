"""
data_cleaning.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Day 2: Clean nav_history, investor_transactions, scheme_performance.
Saves cleaned versions to data/processed/.
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def clean_nav_history():
    """
    Cleans 02_nav_history.csv:
    - Parse dates to datetime
    - Sort by amfi_code + date
    - Validate NAV > 0 (invalid NAVs treated as missing, then forward-filled per fund)
    - Forward-fill any missing/invalid NAV using the previous valid trading day for that fund
    - Remove duplicate (amfi_code, date) rows
    """
    print("Cleaning nav_history...")
    df = pd.read_csv(RAW_DIR / "02_nav_history.csv")
    original_rows = len(df)

    # 1. Parse dates
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")

    # 2. Remove exact duplicate rows first
    duplicates_removed = df.duplicated(subset=['amfi_code', 'date']).sum()
    df = df.drop_duplicates(subset=['amfi_code', 'date'], keep='first')

    # 3. Sort by amfi_code then date - critical for forward-fill and for time-series math later
    df = df.sort_values(['amfi_code', 'date']).reset_index(drop=True)

    # 4. Validate NAV > 0 - treat invalid NAV (<=0 or null) as missing
    invalid_nav_count = (df['nav'] <= 0).sum() + df['nav'].isnull().sum()
    df.loc[df['nav'] <= 0, 'nav'] = np.nan

    # 5. Forward-fill NAV WITHIN each fund's own group (never fill across different funds)
    df['nav'] = df.groupby('amfi_code')['nav'].ffill()

    # If any NAV is still null after forward-fill (e.g. the very first row for a fund was invalid),
    # flag it rather than silently guessing a value
    still_null = df['nav'].isnull().sum()

    # 6. Recompute daily return now that NAV series is clean (useful for Day 4, but easy to add now)
    df['daily_return_pct'] = df.groupby('amfi_code')['nav'].pct_change() * 100

    print(f"  Original rows: {original_rows}")
    print(f"  Duplicate rows removed: {duplicates_removed}")
    print(f"  Invalid NAV (<=0) values found and forward-filled: {invalid_nav_count}")
    print(f"  Rows still null after forward-fill (no prior valid value): {still_null}")
    print(f"  Final rows: {len(df)}")

    output_path = PROCESSED_DIR / "02_nav_history_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"  Saved -> {output_path}\n")

    return df


def clean_investor_transactions():
    """
    Cleans 08_investor_transactions.csv:
    - Standardise transaction_type (strip whitespace, fix casing - defensive, even if already clean)
    - Validate amount_inr > 0
    - Parse transaction_date to datetime
    - Validate kyc_status against expected enum values
    """
    print("Cleaning investor_transactions...")
    df = pd.read_csv(RAW_DIR / "08_investor_transactions.csv")
    original_rows = len(df)

    # 1. Standardise transaction_type: strip whitespace, fix casing
    # (Defensive cleaning - even though current data is already clean, this protects
    #  against future data refreshes that may introduce inconsistent casing/spacing.)
    df['transaction_type'] = df['transaction_type'].str.strip().str.capitalize()
    expected_types = {'Sip', 'Lumpsum', 'Redemption'}
    # Fix "Sip" -> "SIP" since capitalize() would otherwise give us "Sip"
    df['transaction_type'] = df['transaction_type'].replace({'Sip': 'SIP'})

    unexpected_types = set(df['transaction_type'].unique()) - {'SIP', 'Lumpsum', 'Redemption'}
    if unexpected_types:
        print(f"  !! WARNING: unexpected transaction_type values found: {unexpected_types}")
    else:
        print("  transaction_type values: all valid (SIP / Lumpsum / Redemption). PASS.")

    # 2. Validate amount_inr > 0
    invalid_amounts = (df['amount_inr'] <= 0).sum()
    if invalid_amounts > 0:
        print(f"  !! WARNING: {invalid_amounts} rows have amount_inr <= 0. Removing these rows.")
        df = df[df['amount_inr'] > 0]
    else:
        print("  amount_inr validation: all values > 0. PASS.")

    # 3. Parse transaction_date to datetime
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format="%Y-%m-%d")

    # 4. Validate kyc_status enum
    expected_kyc = {'Verified', 'Pending'}
    actual_kyc = set(df['kyc_status'].unique())
    unexpected_kyc = actual_kyc - expected_kyc
    if unexpected_kyc:
        print(f"  !! WARNING: unexpected kyc_status values found: {unexpected_kyc}")
    else:
        print("  kyc_status values: all valid (Verified / Pending). PASS.")

    # 5. Remove exact duplicate transactions (defensive check)
    duplicates_removed = df.duplicated().sum()
    df = df.drop_duplicates()

    print(f"  Original rows: {original_rows}")
    print(f"  Duplicate rows removed: {duplicates_removed}")
    print(f"  Final rows: {len(df)}")

    output_path = PROCESSED_DIR / "08_investor_transactions_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"  Saved -> {output_path}\n")

    return df


def clean_scheme_performance():
    """
    Cleans 07_scheme_performance.csv:
    - Validate all return/risk columns are numeric
    - Check expense_ratio_pct is within expected range (0.1% - 2.5%)
    - Flag anomalies: positive max_drawdown (should always be <= 0), extreme outlier values
    """
    print("Cleaning scheme_performance...")
    df = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")
    original_rows = len(df)

    numeric_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct',
                     'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct',
                     'max_drawdown_pct', 'expense_ratio_pct']

    # 1. Validate numeric - force conversion, anything that fails becomes NaN so we can catch it
    for col in numeric_cols:
        non_numeric_before = df[col].isnull().sum()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        non_numeric_after = df[col].isnull().sum()
        newly_broken = non_numeric_after - non_numeric_before
        if newly_broken > 0:
            print(f"  !! WARNING: {col} had {newly_broken} non-numeric values converted to NaN.")
    print("  Numeric validation complete for all return/risk columns.")

    # 2. Check expense_ratio_pct range (0.1% - 2.5%)
    out_of_range = df[(df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5)]
    if len(out_of_range) > 0:
        print(f"  !! WARNING: {len(out_of_range)} schemes have expense_ratio_pct outside 0.1%-2.5%:")
        print(out_of_range[['amfi_code', 'scheme_name', 'expense_ratio_pct']])
    else:
        print(f"  expense_ratio_pct range check: all {len(df)} schemes within 0.1%-2.5%. PASS.")

    # 3. Flag anomaly: max_drawdown_pct should always be <= 0 (a drawdown is a decline)
    positive_drawdown = df[df['max_drawdown_pct'] > 0]
    if len(positive_drawdown) > 0:
        print(f"  !! ANOMALY: {len(positive_drawdown)} schemes have positive max_drawdown_pct (should be <= 0):")
        print(positive_drawdown[['amfi_code', 'scheme_name', 'max_drawdown_pct']])
    else:
        print("  max_drawdown_pct sanity check: all values <= 0 as expected. PASS.")

    # 4. Flag statistical outliers (beyond 3 standard deviations) for return/risk columns - informational only, not removed
    print("\n  Outlier scan (values beyond 3 std. dev. from mean) - flagged for review, not removed:")
    any_outliers = False
    for col in numeric_cols:
        mean, std = df[col].mean(), df[col].std()
        outliers = df[(df[col] - mean).abs() > 3 * std]
        if len(outliers) > 0:
            any_outliers = True
            print(f"    {col}: {len(outliers)} outlier(s) -> "
                  f"{outliers[['amfi_code', 'scheme_name', col]].to_dict('records')}")
    if not any_outliers:
        print("    No outliers beyond 3 std. dev. found.")

    # 5. Remove exact duplicates (defensive)
    duplicates_removed = df.duplicated().sum()
    df = df.drop_duplicates()

    print(f"\n  Original rows: {original_rows}")
    print(f"  Duplicate rows removed: {duplicates_removed}")
    print(f"  Final rows: {len(df)}")

    output_path = PROCESSED_DIR / "07_scheme_performance_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"  Saved -> {output_path}\n")

    return df


if __name__ == "__main__":
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()