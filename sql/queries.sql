-- ============================================================
-- Bluestock Fintech MF Capstone - Analytical SQL Queries
-- Day 2: 10 queries against bluestock_mf.db
-- ============================================================

-- Q1: Top 5 funds by AUM (using fact_performance, which has scheme-level AUM)
SELECT f.scheme_name, f.fund_house, p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- Q2: Average NAV per month (across all funds, all time)
SELECT d.year, d.month, ROUND(AVG(n.nav), 2) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date_id = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- Q3: SIP inflow YoY growth (month-wise, from industry-level data)
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_industry
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month;

-- Q4: Transactions by state
SELECT state, COUNT(*) AS num_transactions, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- Q5: Funds with expense_ratio < 1%
SELECT scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Q6: Top 5 funds by 3-year return
SELECT f.scheme_name, f.fund_house, p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 5;

-- Q7: Average transaction amount by transaction_type
SELECT transaction_type, COUNT(*) AS num_transactions, ROUND(AVG(amount_inr), 2) AS avg_amount
FROM fact_transactions
GROUP BY transaction_type;

-- Q8: Funds with the highest Sharpe ratio per category
SELECT f.category, f.scheme_name, p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio = (
    SELECT MAX(p2.sharpe_ratio)
    FROM fact_performance p2
    JOIN dim_fund f2 ON p2.amfi_code = f2.amfi_code
    WHERE f2.category = f.category
)
ORDER BY f.category;

-- Q9: Number of schemes and average expense ratio per fund house
SELECT fund_house, COUNT(*) AS num_schemes, ROUND(AVG(expense_ratio_pct), 2) AS avg_expense_ratio
FROM dim_fund
GROUP BY fund_house
ORDER BY num_schemes DESC;

-- Q10: Worst max drawdown per category (which category had the scariest decline)
SELECT f.category, f.scheme_name, p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.max_drawdown_pct = (
    SELECT MIN(p2.max_drawdown_pct)
    FROM fact_performance p2
    JOIN dim_fund f2 ON p2.amfi_code = f2.amfi_code
    WHERE f2.category = f.category
)
ORDER BY p.max_drawdown_pct ASC;