
import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "cleaning_business.db"
SQL_PATH = BASE_DIR / "sql" / "02_customer_retention.sql"

sql_query = SQL_PATH.read_text(encoding="utf-8").strip()

with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(sql_query, conn)

# Display only the first 12 months of each cohort.
df = df[df["months_since_first_booking"] <= 11].copy()

# Convert dates to readable year-month labels.
df["cohort_month"] = pd.to_datetime(
    df["cohort_month"]
).dt.strftime("%Y-%m")

retention_matrix = df.pivot(
    index="cohort_month",
    columns="months_since_first_booking",
    values="retention_pct"
)

fig, ax = plt.subplots(figsize=(14, 12))

image = ax.imshow(
    retention_matrix,
    aspect="auto",
    cmap="YlGnBu",
    vmin=0,
    vmax=100
)

ax.set_xticks(range(len(retention_matrix.columns)))
ax.set_xticklabels(retention_matrix.columns)

ax.set_yticks(range(len(retention_matrix.index)))
ax.set_yticklabels(retention_matrix.index)

ax.set_xlabel("Months Since First Booking")
ax.set_ylabel("Customer Cohort")
ax.set_title(
    "Residential Cleaning Customer Cohort Activity",
    fontsize=15,
    fontweight="bold",
    pad=18
)

fig.colorbar(
    image,
    ax=ax,
    label="Customers Active in Month (%)"
)

plt.tight_layout()

OUTPUT_PATH = BASE_DIR / "reports" / "customer_retention_heatmap.png"

plt.savefig(
    OUTPUT_PATH,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print(f"Heatmap saved to: {OUTPUT_PATH}")
