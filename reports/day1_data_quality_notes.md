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

## Duplicate Rows
- No unexpected duplicate rows found across the 10 datasets at ingestion stage.

## Conclusion
Data is structurally sound and matches the documented schema. No blocking issues for
proceeding to Day 2 (Data Cleaning + SQL Database Design).
