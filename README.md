# Detecting Suspicious FX Transactions: A Rule-Based AML Monitoring Dashboard with Azure & Power BI

Built an end-to-end AML transaction monitoring pipeline using Python to generate 5,000 synthetic FX transactions with embedded suspicious patterns, loaded into Azure SQL Database and flagged using rule-based SQL views covering structuring, high-risk countries, round amounts, and velocity triggers. Created a GDPR-compliant reporting layer by masking personal data through SHA-256 hashing, ensuring Power BI never accesses raw counterparty information. Designed a three-page Power BI dashboard connected to Azure SQL, visualizing compliance KPIs, flagged transaction details with risk scoring, and FX activity breakdowns for non-technical stakeholders.

> **Note:** All data in this project is synthetic. No real company data has been used.

---

## Architecture

```
Python (faker + pandas)  →  Azure SQL Database (free tier)  →  SQL Flagging Views  →  Power BI Dashboard
       ↓                            ↓                                ↓                        ↓
  5,000 synthetic            Single table with              4 rule-based views:         3-page dashboard:
  FX transactions            FX transaction data            - Flagged transactions      - Compliance Overview
  with seeded risk           hosted on Azure                - GDPR-masked reporting     - Flagged Transactions
  patterns                                                  - Daily summary             - FX Activity
```

---

## Tech Stack

- **Python** — Synthetic data generation (pandas, faker)
- **Azure SQL Database** — Cloud-hosted relational database (free tier)
- **SQL** — Rule-based AML flagging views, data validation
- **Power BI** — Interactive dashboards connected to Azure SQL via Import mode
- **DAX** — Custom measures (Flagged %, Avg Flagged Amount)
- **GDPR** — SHA-256 hashing on counterparty names for data minimization

---

## AML Flagging Rules

The SQL view `vw_flagged_transactions` applies four explainable detection rules:

| Rule | Logic | Why it matters |
|---|---|---|
| **Structuring** | Amount between €9,000–€9,999 | Just under the €10k reporting threshold — classic "smurfing" pattern |
| **High-risk country** | Country in watchlist (IR, KP, MM, AF, SY) | Transactions routed through sanctioned or high-risk jurisdictions |
| **Round amounts** | Exact multiples of €5,000 above €5k | Unusual precision suggesting layering or placement activity |
| **Velocity** | Customer with >5 transactions in one day | Rapid movement of funds — potential structuring across transactions |

Each flagged transaction receives a **risk score** weighted by the customer's own risk rating (High = 3, Medium = 2, Low = 1).

**Result:** 375 transactions flagged out of 4,915 total (7.63%).

---

## GDPR Considerations

Power BI connects to `vw_reporting_masked`, never the raw table. Counterparty names are replaced with a truncated SHA-256 hash at the database level, ensuring the reporting layer never exposes personal data. This implements the **data minimization** principle — the dashboard shows everything needed for compliance analysis without any PII.

---

## Dashboard Screenshots

### Page 1 — Compliance Overview
> Cards showing total transactions, flagged count, and flagged %. Line chart of daily volume with flagged overlay. Donut chart breaking down flags by reason. Currency pair slicer for filtering.

![Compliance Overview](Page%201.png)

### Page 2 — Flagged Transaction Detail
> Sortable table of all flagged transactions with conditional formatting on risk score (green/yellow/red). Bar chart showing flags by country. Flag type slicer for filtering by rule.

![Flagged Transactions](Page%202.png)
### Page 3 — FX Activity Breakdown
> Bar chart of transaction volume by currency pair. Donut charts showing distribution by channel and customer risk rating.

![FX Activity](Page%203.png)

---

## Project Files

| File | Description |
|---|---|
| `generate_fx_data.py` | Python script to generate synthetic FX dataset with seeded suspicious patterns |
| `fx_transactions.csv` | Pre-generated dataset (~4,915 rows) |
| `load_to_azure.py` | Python loader to bulk-insert CSV into Azure SQL Database |
| `flagging_rules.sql` | SQL views for AML flagging, GDPR masking, and daily summary |
| `FX_AML_Monitoring.pbix` | Power BI dashboard file |

---

## How to Run

1. **Generate data** — `pip install pandas faker` then `python generate_fx_data.py` (or use the included CSV)
2. **Set up Azure SQL** — Create a free-tier Azure SQL Database, run the CREATE TABLE statement
3. **Load data** — Edit credentials in `load_to_azure.py` and run it
4. **Create views** — Paste `flagging_rules.sql` into the Azure Query Editor and run
5. **Connect Power BI** — Get Data → Azure SQL Database → Import the three views → build dashboards

---

## Context

This project is a simplified rebuild of a compliance dashboard built during a data analyst role at a financial services firm in Dublin. The original used real FX data which cannot be shared, so this version uses synthetic data with the same architecture, flagging logic, and reporting structure.
