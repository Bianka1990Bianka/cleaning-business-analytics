
import sqlite3
from pathlib import Path
import pandas as pd

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "cleaning_business.db"

# Tables to import
tables = [
    "customers",
    "employees",
    "services",
    "bookings",
    "job_assignments",
    "expenses"
]

# Create SQLite database
with sqlite3.connect(DB_PATH) as conn:

    for table in tables:
        csv_path = DATA_DIR / f"{table}.csv"

        df = pd.read_csv(csv_path)

        df.to_sql(
            table,
            conn,
            if_exists="replace",
            index=False
        )

        print(f"{table}: {len(df):,} rows imported")

print("\nDatabase created successfully!")
print(f"Location: {DB_PATH}")
