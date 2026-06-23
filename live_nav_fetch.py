"""
live_nav_fetch.py
Bluestock Fintech - Mutual Fund Analytics Capstone
Day 1: Fetch live NAV history from mfapi.in for HDFC Top 100 + 5 key schemes.
Saves each as a raw CSV in data/raw/.
"""

import requests
import pandas as pd
from pathlib import Path
import time

RAW_DATA_DIR = Path("data/raw")
BASE_URL = "https://api.mfapi.in/mf/"

# Scheme code -> friendly name, for naming output files
SCHEMES = {
    125497: "hdfc_top100",
    119551: "sbi_bluechip",
    120503: "icici_bluechip",
    118632: "nippon_largecap",
    119092: "axis_bluechip",
    120841: "kotak_bluechip",
}


def fetch_scheme_nav(scheme_code: int, max_retries: int = 3, timeout: int = 30) -> dict:
    """
    Calls the mfapi.in API for a single scheme code.
    Retries up to `max_retries` times if the request times out or fails,
    waiting a bit longer between each attempt (simple backoff).
    Returns the parsed JSON response as a Python dict.
    Raises an exception only if all attempts fail.
    """
    url = f"{BASE_URL}{scheme_code}"

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # raises an error if HTTP status is not 200 OK
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise  # out of retries, let the caller handle/log this failure
            wait_seconds = attempt * 3  # 3s, 6s, 9s... gives the server more breathing room each time
            print(f"  Attempt {attempt} failed ({e}). Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)


def save_scheme_as_csv(scheme_code: int, friendly_name: str, json_data: dict):
    """
    Converts the 'data' portion of the API response into a DataFrame
    and saves it as a raw CSV.
    """
    meta = json_data.get("meta", {})
    nav_records = json_data.get("data", [])

    if not nav_records:
        print(f"  !! No NAV data returned for scheme {scheme_code}")
        return

    df = pd.DataFrame(nav_records)

    # Add scheme_code and scheme_name columns so this file is self-describing
    df["amfi_code"] = scheme_code
    df["scheme_name"] = meta.get("scheme_name", "Unknown")
    df["fund_house"] = meta.get("fund_house", "Unknown")

    # Convert date from "DD-MM-YYYY" (API format) to proper datetime, then to ISO format
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

    # Convert nav from string to numeric
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # Sort oldest -> newest, which is more natural for time series analysis later
    df = df.sort_values("date").reset_index(drop=True)

    output_path = RAW_DATA_DIR / f"live_nav_{friendly_name}_{scheme_code}.csv"
    df.to_csv(output_path, index=False)

    print(f"  Saved {len(df)} rows -> {output_path}")
    print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")


def main():
    print("Fetching live NAV data from mfapi.in...\n")

    for scheme_code, friendly_name in SCHEMES.items():
        print(f"Fetching scheme {scheme_code} ({friendly_name})...")
        try:
            json_data = fetch_scheme_nav(scheme_code)
            save_scheme_as_csv(scheme_code, friendly_name, json_data)
        except requests.exceptions.RequestException as e:
            print(f"  !! Network/API error for {scheme_code}: {e}")
        except Exception as e:
            print(f"  !! Unexpected error for {scheme_code}: {e}")

        time.sleep(1)  # small delay between requests - polite to the free public API
        print()

    print("Live NAV fetch complete.")


if __name__ == "__main__":
    main()