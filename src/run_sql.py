
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "cleaning_business.db"
SQL_PATH = BASE_DIR / "sql" / "03_profitability_analysis.sql"

# Read SQL script
sql_script = SQL_PATH.read_text(encoding="utf-8")

# Split statements at semicolons
queries = [
    q.strip()
    for q in sql_script.split(";")
    if q.strip()
]

with sqlite3.connect(DB_PATH) as conn:

    for i, query in enumerate(queries, start=1):
        print(f"\n{'=' * 45}")
        print(f"BUSINESS ANALYSIS QUERY {i}")
        print("=" * 45)

        result = pd.read_sql_query(query, conn)
        print(result.to_string(index=False))
