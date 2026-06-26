"""
load_to_sql.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Day 2: Generate dim_date, create the SQLite schema, and load all cleaned
datasets into bluestock_mf.db using SQLAlchemy.
"""

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

PROCESSED_DIR = Path("data/processed")
SQL_DIR = Path("sql")
DB_PATH = Path("data/db/bluestock_mf.db")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # ensure data/db/ folder exists


def build_dim_date(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Generates a full calendar reference table between start_date and end_date,
    one row per calendar day (not just trading days - dim_date should cover
    every possible date so ANY fact table, including weekends if ever needed,
    can join against it).
    """
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    df = pd.DataFrame({"full_date": dates})
    df["date_id"] = df["full_date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["full_date"].dt.year
    df["month"] = df["full_date"].dt.month
    df["quarter"] = df["full_date"].dt.quarter
    df["day_of_week"] = df["full_date"].dt.day_name()
    df["is_weekday"] = (df["full_date"].dt.weekday < 5).astype(int)  # Mon-Fri = 0-4

    # Reorder columns to match schema.sql column order
    df = df[["date_id", "full_date", "year", "month", "quarter", "day_of_week", "is_weekday"]]
    return df


def add_date_id(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Adds a date_id column (YYYYMMDD integer) derived from an existing date column."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["date_id"] = df[date_col].dt.strftime("%Y%m%d").astype(int)
    return df


def create_schema(engine):
    """Executes schema.sql to create all tables (if they don't already exist)."""
    schema_sql = (SQL_DIR / "schema.sql").read_text()
    with engine.connect() as conn:
        # SQLite allows multiple statements separated by ';' - split and run each
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()
    print("Schema created (6 tables).")


def load_table(engine, df: pd.DataFrame, table_name: str, source_row_count: int):
    """Loads a DataFrame into a SQL table and verifies the row count matches."""
    df.to_sql(table_name, engine, if_exists="append", index=False)

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        db_row_count = result.scalar()

    status = "MATCH" if db_row_count == source_row_count else "MISMATCH"
    print(f"  {table_name}: source={source_row_count} rows, loaded={db_row_count} rows -> {status}")


def main():
    print("Connecting to SQLite database...")
    engine = create_engine(f"sqlite:///{DB_PATH}")

    print("Creating schema...")
    create_schema(engine)

    print("\nLoading dim_fund...")
    fund_master = pd.read_csv(PROCESSED_DIR / "01_fund_master_clean.csv")
    load_table(engine, fund_master, "dim_fund", len(fund_master))

    print("\nBuilding and loading dim_date...")
    # Use a wide enough range to safely cover all datasets (2012 onward, since live NAV fetch went back that far)
    dim_date = build_dim_date("2012-01-01", "2026-12-31")
    load_table(engine, dim_date, "dim_date", len(dim_date))

    print("\nLoading fact_nav...")
    nav_history = pd.read_csv(PROCESSED_DIR / "02_nav_history_clean.csv")
    nav_history = add_date_id(nav_history, "date")
    load_table(engine, nav_history, "fact_nav", len(nav_history))

    print("\nLoading fact_transactions...")
    transactions = pd.read_csv(PROCESSED_DIR / "08_investor_transactions_clean.csv")
    transactions = add_date_id(transactions, "transaction_date")
    load_table(engine, transactions, "fact_transactions", len(transactions))

    print("\nLoading fact_performance...")
    performance = pd.read_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv")
    # fact_performance only needs columns defined in schema.sql - drop the extras
    # that scheme_performance.csv also carries (scheme_name, fund_house, category, plan)
    # since those already live in dim_fund.
    perf_cols = ["amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                 "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
                 "std_dev_ann_pct", "max_drawdown_pct", "aum_crore", "expense_ratio_pct",
                 "morningstar_rating", "risk_grade"]
    performance = performance[perf_cols]
    load_table(engine, performance, "fact_performance", len(performance))

    print("\nLoading fact_aum...")
    aum = pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house_clean.csv")
    aum = add_date_id(aum, "date")
    load_table(engine, aum, "fact_aum", len(aum))

    print("\nAll tables loaded successfully.")


if __name__ == "__main__":
    main()