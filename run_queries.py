"""
run_queries.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Day 2: Execute all queries in sql/queries.sql against bluestock_mf.db
and print results, to verify each query is correct before submission.
"""

import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

DB_PATH = Path("data/db/bluestock_mf.db")
QUERIES_PATH = Path("sql/queries.sql")


def split_queries(sql_text: str):
    """
    Splits the queries.sql file into individual (comment_label, query) pairs.
    Assumes each query is preceded by a '-- Qn: description' comment line.
    """
    blocks = []
    current_label = None
    current_sql_lines = []

    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- Q") and ":" in stripped:
            # Save the previous block before starting a new one
            if current_label and current_sql_lines:
                blocks.append((current_label, "\n".join(current_sql_lines).strip()))
            current_label = stripped.lstrip("- ").strip()
            current_sql_lines = []
        elif stripped.startswith("--"):
            continue  # skip other comment lines (like the NOTE under old Q3)
        elif stripped:
            current_sql_lines.append(line)

    if current_label and current_sql_lines:
        blocks.append((current_label, "\n".join(current_sql_lines).strip()))

    return blocks


def main():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    sql_text = QUERIES_PATH.read_text()
    query_blocks = split_queries(sql_text)

    print(f"Found {len(query_blocks)} queries to run.\n")

    for label, query_sql in query_blocks:
        print("=" * 70)
        print(label)
        print("=" * 70)
        try:
            result_df = pd.read_sql(query_sql, engine)
            print(result_df.to_string(index=False))
        except Exception as e:
            print(f"!! ERROR running this query: {e}")
        print()


if __name__ == "__main__":
    main()