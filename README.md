# Bluestock Fintech — Mutual Fund Analytics Platform
**Capstone Project | Data Engineering + Analytics + BI Dashboard**

---

## Project Overview

An end-to-end Mutual Fund Analytics Platform built for Bluestock Fintech Pvt. Ltd.,
covering the full data pipeline: Extract → Transform → Load → Analyse → Visualise.

The platform ingests publicly available AMFI India mutual fund data, transforms it
through a robust ETL pipeline, stores it in a relational SQLite database, performs
comprehensive EDA and performance analytics, and presents insights via an interactive
Power BI dashboard.

**Dataset:** 40 mutual fund schemes across 10 fund houses | ~46,000 NAV records |
~32,000 investor transactions | 4.5 years of history (Jan 2022 – May 2026)

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/<VelociraptorSR>/bluestock-mf-capstone.git
cd bluestock-mf-capstone
```

### 2. Set up environment
```bash
python -m venv venv
.\venv\Scripts\Activate     # Windows
pip install -r requirements.txt
```

### 3. Run the full ETL pipeline
```bash
python scripts/etl_pipeline.py
```

### 4. Open the dashboard
Open `dashboard/bluestock_mf_dashboard.pbix` in Power BI Desktop.

---

## Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/              # Original CSV datasets (10 files)
│   ├── processed/        # Cleaned datasets (10 files)
│   └── db/               # SQLite database (not committed — see schema.sql)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py       # Master ETL runner
│   ├── live_nav_fetch.py     # mfapi.in live NAV fetcher
│   ├── compute_metrics.py    # Performance metrics computation
│   └── recommender.py        # Fund recommendation engine
├── sql/
│   ├── schema.sql            # CREATE TABLE statements (7 tables)
│   └── queries.sql           # 10 analytical SQL queries
├── dashboard/
│   └── bluestock_mf_dashboard.pbix
├── reports/
│   ├── Final_Report.pdf
│   ├── Presentation.pptx
│   ├── day1_data_quality_notes.md
│   └── charts/               # 13 exported chart PNGs
├── data_ingestion.py         # Day 1: Load + validate raw datasets
├── data_cleaning.py          # Day 2: Clean + save processed datasets
├── load_to_sql.py            # Day 2: Build SQLite database
├── run_queries.py            # Day 2: Execute + verify SQL queries
├── requirements.txt
└── README.md
```

---

## Key Deliverables

| # | Deliverable | Location |
|---|---|---|
| D1 | ETL Pipeline | `scripts/etl_pipeline.py` |
| D2 | SQLite Database | `data/db/bluestock_mf.db` (schema: `sql/schema.sql`) |
| D3 | EDA Notebook | `notebooks/03_eda_analysis.ipynb` |
| D4 | Performance Analytics | `notebooks/04_performance_analytics.ipynb` |
| D5 | Power BI Dashboard | `dashboard/bluestock_mf_dashboard.pbix` |
| D6 | Advanced Analytics | `notebooks/05_advanced_analytics.ipynb` |
| D7 | Final Report + Slides | `reports/Final_Report.pdf` + `reports/Presentation.pptx` |

---

## Database Schema

7-table SQLite star schema:

| Table | Type | Rows |
|---|---|---|
| `dim_fund` | Dimension | 40 |
| `dim_date` | Dimension | 5,479 |
| `fact_nav` | Fact | 46,000 |
| `fact_transactions` | Fact | 32,778 |
| `fact_performance` | Fact | 40 |
| `fact_aum` | Fact | 90 |
| `fact_sip_industry` | Fact | 48 |

---

## Key Findings

1. **SBI Mutual Fund dominates industry AUM** at ₹12.50 lakh crore (Dec 2025),
   confirmed against real AMFI published data.
2. **Monthly SIP inflows hit ₹31,002 crore** (Dec 2025 all-time high), up from
   ~₹11,500 crore in Jan 2022 — a 2.7× growth over 4 years.
3. **Small Cap funds carry highest tail risk** — top 5 worst VaR (95%) all belong
   to Small Cap funds, with SBI Small Cap Direct at -2.69% daily VaR.
4. **Benchmark independence discovered** — `nav_history.csv` and
   `benchmark_indices.csv` are statistically independent (avg |r| = 0.02 across
   all 40 funds), documented transparently rather than producing misleading
   Alpha/Beta figures.
5. **97.8% SIP at-risk rate** — investors average 64.89-day gaps between SIP
   payments vs the expected ~30-day monthly cadence, with no demographic
   concentration — suggesting systematic rather than demographic-specific dropout.
6. **Axis Bluechip Fund is the most concentrated portfolio** by sector HHI (2,968),
   counterintuitively higher than any Small Cap fund in the dataset.

---

## Important Notes on Dataset Integrity

Several findings emerged from cross-validating computed metrics against
the provided `scheme_performance.csv`:

- **Sharpe/Sortino ratios** are unreliable for Liquid/Debt funds due to near-zero
  excess return instability — provided values used for these.
- **Alpha/Beta vs NIFTY100** show near-zero correlation (r ≈ 0.02) for all funds,
  confirmed visually — NAV and benchmark were independently generated.
- **Max Drawdown** was recomputed from raw NAV (values verified visually against
  actual NAV charts) as the provided column showed inconsistencies.

Full methodology notes: `reports/day1_data_quality_notes.md`

---

## Technologies Used

Python 3.13 | Pandas | NumPy | Matplotlib | Seaborn | Plotly | SQLite |
SQLAlchemy | SciPy | Jupyter Lab | Power BI Desktop | Git/GitHub

---

## Data Sources

AMFI India (amfiindia.com) | mfapi.in REST API | NSE/BSE public data
All data is publicly available. This project is for educational purposes only
and does not constitute financial advice.

---

*Bluestock Fintech Pvt. Ltd. | Intern Capstone Project | June 2026*
