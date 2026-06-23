# Day 1 — Data Quality Summary
Bluestock Fintech MF Capstone

## Datasets Loaded
All 10 provided CSV files loaded successfully with `pandas.read_csv()`.
Row counts matched expectations from the project specification (page 5-6 of project doc).

## Observations / Anomalies

### 1. Missing values — `04_monthly_sip_inflows.csv`
- Column `yoy_growth_pct` has 12 missing values.
- **Root cause (expected, not an error):** This column represents Year-over-Year growth,
  which requires a value from 12 months prior to compute. The dataset's first 12 rows
  (first year of data) have no prior-year value to compare against, so YoY growth is
  undefined for those rows.
- **Action:** No fix needed at ingestion stage. These nulls are legitimate and will remain
  null unless earlier historical data becomes available. Will NOT be filled with 0 or any
  placeholder, since that would misrepresent actual growth.

### 2. Date columns loaded as string/object dtype (all files with date columns)
- All date columns (e.g. `date`, `transaction_date`, `month`, `launch_date`) are currently
  stored as Python `str`/object type, not as proper `datetime64` type, even though the
  values are correctly formatted (e.g. `2022-03-31`).
- **Root cause (expected):** `pandas.read_csv()` does not auto-detect dates unless told to.
- **Action deferred to Day 2:** Per project plan, date parsing to proper `datetime` type is
  a Day 2 task ("Clean nav_history.csv: Parse dates to datetime"). Will be handled then
  using `pd.to_datetime()`.

### 3. Category coverage — `01_fund_master.csv`
- The project document (page 4, page 7) describes three fund categories: Equity, Debt,
  Hybrid. The actual `fund_master` data only contains **Equity (34 schemes)** and
  **Debt (6 schemes)** — no Hybrid schemes are present among the 40.
- **Action:** No fix needed. Documented as an observation; all downstream analysis will
  only ever see Equity/Debt category values for this dataset.

### 4. Risk category granularity — `01_fund_master.csv`
- The document's appendix (page 20) lists 4 risk categories: Low / Moderate / High /
  Very High. The actual data has 5 distinct values, including an additional
  **"Moderately High"** tier.
- **Action:** No fix needed — just noted, since any chart or filter using risk_category
  should account for 5 values, not 4.

## Duplicate Rows
- No unexpected duplicate rows found across the 10 datasets at ingestion stage.

## AMFI Code Validation (fund_master vs nav_history)
- fund_master: 40 unique amfi_codes
- nav_history: 40 unique amfi_codes
- Result: **PASS** — every code in fund_master has matching nav_history data, and there
  are no orphan codes in nav_history that don't exist in fund_master.
- This confirms a clean 1-to-1 relationship between the two datasets, which will support
  a reliable foreign key join (`dim_fund.amfi_code` -> `fact_nav.amfi_code`) when building
  the SQL schema on Day 2.

## Conclusion
Data is structurally sound and matches the documented schema. No blocking issues for
proceeding to Day 2 (Data Cleaning + SQL Database Design).
