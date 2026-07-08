"""
compute_metrics.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Computes all performance metrics from cleaned NAV data:
- CAGR (1yr, 3yr, 5yr)
- Max Drawdown
- VaR and CVaR (95%)
Saves outputs to project root as CSVs.
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
TRADING_DAYS = 252
RISK_FREE_RATE = 0.065


def compute_cagr(fund_nav_df, years):
    fund_nav_df = fund_nav_df.sort_values('date')
    end_date = fund_nav_df['date'].max()
    end_nav = fund_nav_df.loc[fund_nav_df['date'] == end_date, 'nav'].values[0]
    target_start = end_date - pd.DateOffset(years=years)
    candidates = fund_nav_df[fund_nav_df['date'] >= target_start]
    if candidates.empty:
        return None, None
    start_row = candidates.iloc[0]
    actual_years = (end_date - start_row['date']).days / 365.25
    if actual_years <= 0 or start_row['nav'] <= 0:
        return None, None
    cagr = (end_nav / start_row['nav']) ** (1 / actual_years) - 1
    return cagr * 100, round(actual_years, 2)


def compute_max_drawdown(fund_nav_df):
    fund_nav_df = fund_nav_df.sort_values('date').copy()
    fund_nav_df['running_max'] = fund_nav_df['nav'].cummax()
    fund_nav_df['drawdown'] = fund_nav_df['nav'] / fund_nav_df['running_max'] - 1
    trough_idx = fund_nav_df['drawdown'].idxmin()
    trough_row = fund_nav_df.loc[trough_idx]
    max_dd = trough_row['drawdown'] * 100
    trough_date = trough_row['date']
    peak_nav = trough_row['running_max']
    peak_candidates = fund_nav_df[(fund_nav_df['nav'] == peak_nav) & (fund_nav_df['date'] <= trough_date)]
    peak_date = peak_candidates['date'].max() if not peak_candidates.empty else None
    return max_dd, peak_date, trough_date


def compute_var_cvar(returns_series, confidence=0.95):
    returns = returns_series.dropna() / 100
    var = np.percentile(returns, (1 - confidence) * 100)
    cvar = returns[returns <= var].mean()
    return var * 100, cvar * 100


def main():
    nav_history = pd.read_csv(PROCESSED_DIR / "02_nav_history_clean.csv", parse_dates=['date'])
    fund_master = pd.read_csv(PROCESSED_DIR / "01_fund_master_clean.csv")

    results = []
    for amfi_code in fund_master['amfi_code']:
        fund_nav = nav_history[nav_history['amfi_code'] == amfi_code]
        returns = fund_nav['daily_return_pct']

        cagr_1yr, _ = compute_cagr(fund_nav, 1)
        cagr_3yr, _ = compute_cagr(fund_nav, 3)
        cagr_5yr, years_5yr = compute_cagr(fund_nav, 5)
        max_dd, peak_date, trough_date = compute_max_drawdown(fund_nav)
        var_95, cvar_95 = compute_var_cvar(returns)

        results.append({
            'amfi_code': amfi_code,
            'cagr_1yr_pct': cagr_1yr,
            'cagr_3yr_pct': cagr_3yr,
            'cagr_5yr_pct': cagr_5yr,
            'actual_years_5yr': years_5yr,
            'max_drawdown_pct': max_dd,
            'peak_date': peak_date,
            'trough_date': trough_date,
            'var_95_pct': var_95,
            'cvar_95_pct': cvar_95
        })

    metrics_df = pd.DataFrame(results)
    metrics_df = metrics_df.merge(fund_master[['amfi_code', 'scheme_name']], on='amfi_code')
    metrics_df.to_csv("var_cvar_report.csv", index=False)
    print(f"Saved var_cvar_report.csv ({len(metrics_df)} funds)")


if __name__ == "__main__":
    main()