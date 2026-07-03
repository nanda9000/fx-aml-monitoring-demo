"""
Generate a synthetic FX transaction dataset for the AML monitoring demo.
Creates fx_transactions.csv (~5,000 rows) with deliberately seeded
suspicious patterns: structuring, high-risk countries, round amounts,
and high-velocity customers.

Usage:  pip install pandas faker
        python generate_fx_data.py
"""

import random
from datetime import date, timedelta, time

import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

N_NORMAL = 4600
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 6, 30)

CURRENCY_PAIRS = ["EUR/USD", "EUR/GBP", "GBP/USD", "EUR/JPY", "USD/JPY", "EUR/CHF"]
NORMAL_COUNTRIES = ["IE", "GB", "DE", "FR", "NL", "ES", "IT", "US", "PL", "BE"]
HIGH_RISK_COUNTRIES = ["IR", "KP", "MM", "AF", "SY"]
CHANNELS = ["Online", "Branch", "API"]
RISK_RATINGS = ["Low", "Low", "Low", "Medium", "Medium", "High"]  # weighted

customers = {
    f"CUST-{i:04d}": random.choice(RISK_RATINGS) for i in range(1, 301)
}
customer_ids = list(customers.keys())


def random_date():
    delta = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=random.randint(0, delta))


def random_time():
    return time(random.randint(7, 21), random.randint(0, 59), random.randint(0, 59))


def base_row(txn_id, cust_id, amount, country, txn_date=None, txn_time=None):
    return {
        "transaction_id": f"TXN-{txn_id:06d}",
        "txn_date": (txn_date or random_date()).isoformat(),
        "txn_time": (txn_time or random_time()).strftime("%H:%M:%S"),
        "customer_id": cust_id,
        "counterparty_name": fake.company(),
        "currency_pair": random.choice(CURRENCY_PAIRS),
        "amount_eur": amount,
        "country": country,
        "channel": random.choice(CHANNELS),
        "customer_risk_rating": customers[cust_id],
    }


rows = []
txn_id = 1

# 1) Normal transactions: log-normal-ish amounts, normal countries
for _ in range(N_NORMAL):
    amount = round(random.lognormvariate(7.5, 1.1), 2)  # mostly €500–€15k
    amount = min(amount, 250_000.00)
    rows.append(
        base_row(txn_id, random.choice(customer_ids), amount, random.choice(NORMAL_COUNTRIES))
    )
    txn_id += 1

# 2) Structuring pattern: ~100 txns just under the €10k threshold
for _ in range(100):
    amount = round(random.uniform(9000, 9999), 2)
    rows.append(
        base_row(txn_id, random.choice(customer_ids), amount, random.choice(NORMAL_COUNTRIES))
    )
    txn_id += 1

# 3) High-risk country transactions: ~75
for _ in range(75):
    amount = round(random.uniform(1000, 80000), 2)
    rows.append(
        base_row(txn_id, random.choice(customer_ids), amount, random.choice(HIGH_RISK_COUNTRIES))
    )
    txn_id += 1

# 4) Round amounts: ~60 exact multiples of €5,000
for _ in range(60):
    amount = float(random.choice([5000, 10000, 15000, 20000, 50000, 100000]))
    rows.append(
        base_row(txn_id, random.choice(customer_ids), amount, random.choice(NORMAL_COUNTRIES))
    )
    txn_id += 1

# 5) Velocity pattern: 8 customers each doing 8-12 txns on a single day
for _ in range(8):
    cust = random.choice(customer_ids)
    burst_day = random_date()
    for _ in range(random.randint(8, 12)):
        amount = round(random.uniform(500, 6000), 2)
        rows.append(
            base_row(txn_id, cust, amount, random.choice(NORMAL_COUNTRIES),
                     txn_date=burst_day)
        )
        txn_id += 1

df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv("fx_transactions.csv", index=False)

print(f"Wrote fx_transactions.csv with {len(df):,} rows")
print(df.head(10).to_string(index=False))
