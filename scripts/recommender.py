"""
recommender.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Day 6: Simple fund recommender based on investor risk appetite.
Input: risk appetite (Low / Moderate / High)
Output: top 3 funds by Sharpe ratio within matching risk_grade
"""

import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed")


def load_data():
    """Load fund master and performance data."""
    fund_master = pd.read_csv(PROCESSED_DIR / "01_fund_master_clean.csv")
    performance = pd.read_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv")
    merged = fund_master.merge(
        performance[['amfi_code', 'sharpe_ratio', 'return_3yr_pct']],
        on='amfi_code'
    )
    return merged


def get_recommendations(risk_appetite: str, data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns top 3 funds matching the investor's risk appetite,
    ranked by Sharpe ratio (higher = better risk-adjusted return).

    Risk appetite mapping:
    - Low    -> risk_category in ['Low', 'Moderate']
    - Moderate -> risk_category in ['Moderate', 'Moderately High']
    - High   -> risk_category in ['High', 'Very High']
    """
    risk_appetite = risk_appetite.strip().title()

    risk_mapping = {
        'Low': ['Low', 'Moderate'],
        'Moderate': ['Moderate', 'Moderately High'],
        'High': ['High', 'Very High']
    }

    if risk_appetite not in risk_mapping:
        print(f"Invalid risk appetite '{risk_appetite}'. Choose from: Low, Moderate, High")
        return pd.DataFrame()

    matching_grades = risk_mapping[risk_appetite]
    filtered = data[data['risk_category'].isin(matching_grades)].copy()

    if filtered.empty:
        print(f"No funds found for risk appetite: {risk_appetite}")
        return pd.DataFrame()

    top3 = filtered.nlargest(3, 'sharpe_ratio')[
        ['scheme_name', 'fund_house', 'risk_category',
         'sharpe_ratio', 'return_3yr_pct']
    ].reset_index(drop=True)

    top3.index += 1  # rank starts at 1
    return top3


def main():
    data = load_data()

    print("=" * 60)
    print("BLUESTOCK FINTECH — FUND RECOMMENDER")
    print("=" * 60)

    for appetite in ['Low', 'Moderate', 'High']:
        print(f"\nRisk Appetite: {appetite.upper()}")
        print("-" * 60)
        recs = get_recommendations(appetite, data)
        if not recs.empty:
            print(recs.to_string())
        print()


if __name__ == "__main__":
    main()