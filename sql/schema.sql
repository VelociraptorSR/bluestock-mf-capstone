-- ============================================================
-- Bluestock Fintech MF Capstone - SQLite Star Schema
-- Day 2: Database Design
-- ============================================================

-- ------------------------------------------------------------
-- DIMENSION TABLE: dim_fund
-- One row per mutual fund scheme. Describes the "what" - 
-- referenced by all fact tables via amfi_code.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           TEXT PRIMARY KEY,
    fund_house          TEXT NOT NULL,
    scheme_name         TEXT NOT NULL,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         DATE,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      REAL,
    min_lumpsum_amount  REAL,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

-- ------------------------------------------------------------
-- DIMENSION TABLE: dim_date
-- One row per calendar date. date_id is a readable surrogate
-- key in YYYYMMDD integer format (e.g. 20220103).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_id      INTEGER PRIMARY KEY,   -- e.g. 20220103
    full_date    DATE NOT NULL,         -- e.g. 2022-01-03
    year         INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    day_of_week  TEXT NOT NULL,         -- e.g. 'Monday'
    is_weekday   INTEGER NOT NULL       -- 1 = weekday, 0 = weekend
);

-- ------------------------------------------------------------
-- FACT TABLE: fact_nav
-- One row per (fund, date) - the daily NAV value.
-- Stores both the raw date AND date_id (per design decision)
-- for easier direct querying without forcing a join every time.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code         TEXT NOT NULL,
    date              DATE NOT NULL,
    date_id           INTEGER NOT NULL,
    nav               REAL NOT NULL,
    daily_return_pct  REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

-- ------------------------------------------------------------
-- FACT TABLE: fact_transactions
-- One row per investor transaction (SIP / Lumpsum / Redemption).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT NOT NULL,
    amfi_code           TEXT NOT NULL,
    transaction_date    DATE NOT NULL,
    date_id             INTEGER NOT NULL,
    transaction_type    TEXT NOT NULL,   -- SIP / Lumpsum / Redemption
    amount_inr          REAL NOT NULL,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

-- ------------------------------------------------------------
-- FACT TABLE: fact_performance
-- One row per fund - computed performance/risk metrics.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code           TEXT PRIMARY KEY,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           REAL,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- ------------------------------------------------------------
-- FACT TABLE: fact_aum
-- One row per (fund house, date) - quarterly AUM by fund house.
-- Note: references fund_house directly, NOT amfi_code, since
-- AUM here is reported at the fund-house level, not per-scheme.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_aum (
    fund_house        TEXT NOT NULL,
    date              DATE NOT NULL,
    date_id           INTEGER NOT NULL,
    aum_crore         REAL NOT NULL,
    aum_lakh_crore    REAL,
    num_schemes       INTEGER,
    PRIMARY KEY (fund_house, date),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);


-- ------------------------------------------------------------
-- FACT TABLE: fact_sip_industry
-- One row per month - industry-wide SIP inflow statistics.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month                       TEXT PRIMARY KEY,  -- format YYYY-MM
    sip_inflow_crore            REAL NOT NULL,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);