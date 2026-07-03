-- =============================================================
-- FX AML Demo: flagging rules + masked reporting layer
-- Run against the fxdemo Azure SQL Database after loading data
-- =============================================================

-- ---------------------------------------------------------
-- 1) Flagged transactions view: four explainable rules
--    Each rule gets a flag_reason; risk_score is weighted
--    by the customer's own risk rating.
-- ---------------------------------------------------------
CREATE OR ALTER VIEW vw_flagged_transactions AS
WITH velocity AS (
    -- customers with more than 5 transactions on the same day
    SELECT customer_id, txn_date, COUNT(*) AS txns_that_day
    FROM fx_transactions
    GROUP BY customer_id, txn_date
    HAVING COUNT(*) > 5
),
flags AS (
    SELECT
        t.transaction_id,
        t.txn_date,
        t.customer_id,
        t.currency_pair,
        t.amount_eur,
        t.country,
        t.channel,
        t.customer_risk_rating,
        CASE
            WHEN t.amount_eur BETWEEN 9000 AND 9999.99
                THEN 'Structuring: just under EUR 10k threshold'
            WHEN t.country IN ('IR','KP','MM','AF','SY')
                THEN 'High-risk country'
            WHEN t.amount_eur >= 5000 AND t.amount_eur % 5000 = 0
                THEN 'Round amount (multiple of EUR 5k)'
            WHEN v.customer_id IS NOT NULL
                THEN 'Velocity: >5 transactions in one day'
        END AS flag_reason,
        v.txns_that_day
    FROM fx_transactions t
    LEFT JOIN velocity v
        ON v.customer_id = t.customer_id
       AND v.txn_date    = t.txn_date
)
SELECT
    transaction_id,
    txn_date,
    customer_id,
    currency_pair,
    amount_eur,
    country,
    channel,
    customer_risk_rating,
    flag_reason,
    -- simple weighted score: base 1 per flag, x2 for High-risk customers
    CASE customer_risk_rating
        WHEN 'High'   THEN 3
        WHEN 'Medium' THEN 2
        ELSE 1
    END AS risk_score
FROM flags
WHERE flag_reason IS NOT NULL;
GO

-- ---------------------------------------------------------
-- 2) GDPR-masked reporting view: Power BI reads THIS,
--    never the raw table. counterparty_name is replaced
--    with a one-way hash (pseudonymization / data
--    minimization).
-- ---------------------------------------------------------
CREATE OR ALTER VIEW vw_reporting_masked AS
SELECT
    transaction_id,
    txn_date,
    txn_time,
    customer_id,
    CONVERT(VARCHAR(16),
        HASHBYTES('SHA2_256', counterparty_name), 2) AS counterparty_ref,
    currency_pair,
    amount_eur,
    country,
    channel,
    customer_risk_rating
FROM fx_transactions;
GO

-- ---------------------------------------------------------
-- 3) Daily summary for the Power BI trend page
-- ---------------------------------------------------------
CREATE OR ALTER VIEW vw_daily_summary AS
SELECT
    t.txn_date,
    COUNT(*)                        AS total_txns,
    SUM(t.amount_eur)               AS total_volume_eur,
    COUNT(f.transaction_id)         AS flagged_txns
FROM fx_transactions t
LEFT JOIN vw_flagged_transactions f
    ON f.transaction_id = t.transaction_id
GROUP BY t.txn_date;
GO

-- ---------------------------------------------------------
-- Quick checks
-- ---------------------------------------------------------
-- SELECT flag_reason, COUNT(*) AS n FROM vw_flagged_transactions GROUP BY flag_reason;
-- SELECT TOP 10 * FROM vw_reporting_masked;
-- SELECT TOP 10 * FROM vw_daily_summary ORDER BY txn_date;
