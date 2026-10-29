
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "cleaning_business.db"
CSV_PATH = BASE_DIR / "data" / "expenses.csv"

# Read updated operating expenses
expenses = pd.read_csv(CSV_PATH)

# Update only the expenses table
with sqlite3.connect(DB_PATH) as conn:
    expenses.to_sql(
        "expenses",
        conn,
        if_exists="replace",
        index=False
    )

    result = pd.read_sql_query(
        """
        SELECT
            COUNT(*) AS expense_records,
            ROUND(SUM(amount), 2) AS total_expenses
        FROM expenses
        """,
        conn
    )

print("\nExpenses table updated successfully!")
print(result.to_string(index=False))
