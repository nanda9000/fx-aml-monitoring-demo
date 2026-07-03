"""
Load fx_transactions.csv into the Azure SQL Database.

Usage:  pip install pandas sqlalchemy pyodbc
        (also install "ODBC Driver 17 for SQL Server" from Microsoft)
        Edit the connection settings below, then:
        python load_to_azure.py
"""

import urllib.parse

import pandas as pd
from sqlalchemy import create_engine

# ---- EDIT THESE ----
SERVER   = "rg-fx-server.database.windows.net"
DATABASE = "fx-demo"
USERNAME = "fx-demo"
PASSWORD = "Portal.01"
# --------------------

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};"
    f"UID={USERNAME};PWD={PASSWORD};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

df = pd.read_csv("fx_transactions.csv")
print(f"Loading {len(df):,} rows into fx_transactions...")

df.to_sql("fx_transactions", engine, if_exists="append", index=False, chunksize=500)

with engine.connect() as conn:
    count = conn.exec_driver_sql("SELECT COUNT(*) FROM fx_transactions").scalar()
print(f"Done. Table now has {count:,} rows.")
