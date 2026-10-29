
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Load existing data without regenerating it
bookings = pd.read_csv(DATA_DIR / "bookings.csv")
job_assignments = pd.read_csv(
    DATA_DIR / "job_assignments.csv"
)

completed_bookings = bookings[
    bookings["status"] == "Completed"
].copy()

completed_bookings["month"] = pd.to_datetime(
    completed_bookings["booking_date"]
).dt.to_period("M")

monthly_jobs = completed_bookings.groupby("month").size()

monthly_revenue = completed_bookings.groupby(
    "month"
)["price"].sum()

monthly_labor = job_assignments.merge(
    completed_bookings[["booking_id", "month"]],
    on="booking_id",
    how="inner"
).groupby("month")["labor_cost"].sum()

expense_records = []
expense_id = 60001

months = pd.date_range(
    start="2023-01-01",
    end="2025-12-01",
    freq="MS"
)

for month in months:

    period = month.to_period("M")

    jobs = int(monthly_jobs.get(period, 0))
    revenue = float(monthly_revenue.get(period, 0))
    labor = float(monthly_labor.get(period, 0))

    category_amounts = {
        "Cleaning Supplies": jobs * 9.00,
        "Transportation": jobs * 12.00,
        "Insurance": 500 + jobs * 0.75,
        "Marketing": 600 + revenue * 0.04,
        "Administration": 1200 + jobs * 2.50,
        "Equipment": 250 + jobs * 1.50,
        "Employer Payroll Burden": labor * 0.12
    }

    for category, amount in category_amounts.items():

        expense_records.append({
            "expense_id": expense_id,
            "expense_date": month,
            "category": category,
            "amount": round(amount, 2)
        })

        expense_id += 1

expenses = pd.DataFrame(expense_records)

expenses.to_csv(
    DATA_DIR / "expenses.csv",
    index=False
)

print("\nOperating expenses updated successfully!")
print(f"Total expense records: {len(expenses)}")
print(
    f"Total operating expenses: "
    f"${expenses['amount'].sum():,.2f}"
)

