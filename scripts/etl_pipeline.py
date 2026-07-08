"""
etl_pipeline.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Master ETL pipeline: runs the complete Extract -> Transform -> Load sequence.
Usage: python scripts/etl_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent  # project root, regardless of where script is called from


def run_step(script_path: str, description: str):
    """Run a Python script as a subprocess and report success/failure."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, str(ROOT / script_path)],
        capture_output=False
    )
    if result.returncode != 0:
        print(f"!! FAILED: {description} (exit code {result.returncode})")
        sys.exit(1)
    print(f"COMPLETED: {description}")


def main():
    print("BLUESTOCK FINTECH — MASTER ETL PIPELINE")
    print("Starting full Extract -> Transform -> Load sequence...\n")

    # Step 1: Ingest raw data
    run_step("data_ingestion.py", "Step 1: Data Ingestion (load raw CSVs + validate)")

    # Step 2: Fetch live NAV data
    run_step("scripts/live_nav_fetch.py", "Step 2: Live NAV Fetch (mfapi.in API)")

    # Step 3: Clean all datasets
    run_step("data_cleaning.py", "Step 3: Data Cleaning (validate + save to processed/)")

    # Step 4: Load into SQLite
    run_step("load_to_sql.py", "Step 4: Load to SQLite (create schema + insert data)")

    print(f"\n{'='*60}")
    print("ETL PIPELINE COMPLETE — All steps succeeded.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()