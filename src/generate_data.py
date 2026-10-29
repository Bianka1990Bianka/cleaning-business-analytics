
from pathlib import Path
import numpy as np
import pandas as pd

# Set project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Make the results reproducible
rng = np.random.default_rng(42)

# Create 750 fictional customers
n_customers = 750

customers = pd.DataFrame({
    "customer_id": range(1001, 1001 + n_customers),
    "signup_date": pd.to_datetime(
        rng.choice(
            pd.date_range("2023-01-01", "2025-12-31"),
            size=n_customers
        )
    ),
    "zip_code": rng.choice(
        ["33569", "33578", "33579", "33598", "33619"],
        size=n_customers
    ),
    "cleaning_frequency": rng.choice(
        ["Weekly", "Biweekly", "Monthly", "One-time"],
        size=n_customers,
        p=[0.20, 0.40, 0.20, 0.20]
    )
})

# Save to CSV
output_file = DATA_DIR / "customers.csv"
customers.to_csv(output_file, index=False)

print("Customer dataset created successfully!")
print(f"Total customers: {len(customers)}")
print(customers.head())


# ---------------------------------
# EMPLOYEE DATASET
# ---------------------------------

n_employees = 25

employees = pd.DataFrame({
    "employee_id": range(2001, 2001 + n_employees),
    "hire_date": pd.to_datetime(
        rng.choice(
            pd.date_range("2022-01-01", "2025-06-30"),
            size=n_employees
        )
    ),
    "hourly_wage": rng.uniform(
        15, 23, size=n_employees
    ).round(2),
    "employment_status": rng.choice(
        ["Active", "Inactive"],
        size=n_employees,
        p=[0.85, 0.15]
    )
})

employees.to_csv(
    DATA_DIR / "employees.csv",
    index=False
)

print("\nEmployee dataset created successfully!")
print(f"Total employees: {len(employees)}")
print(employees.head())


# ---------------------------------
# CLEANING SERVICES DATASET
# ---------------------------------

services = pd.DataFrame({
    "service_id": [301, 302, 303, 304],
    "service_name": [
        "Standard Cleaning",
        "Deep Cleaning",
        "Move-In/Move-Out",
        "Recurring Maintenance"
    ],
    "base_price": [150, 275, 350, 120],
    "estimated_hours": [3, 5, 6, 2.5]
})

services.to_csv(
    DATA_DIR / "services.csv",
    index=False
)

print("\nCleaning services dataset created successfully!")
print(services)


# ---------------------------------
# CLEANING BOOKINGS DATASET
# ---------------------------------


# ---------------------------------
# REALISTIC RECURRING BOOKINGS
# ---------------------------------

booking_records = []
booking_id = 40001
end_date = pd.Timestamp("2025-12-31")

frequency_days = {
    "Weekly": 7,
    "Biweekly": 14,
    "Monthly": 30
}

service_prices = services.set_index(
    "service_id"
)["base_price"].to_dict()

for customer in customers.itertuples(index=False):

    signup = pd.Timestamp(customer.signup_date)
    frequency = customer.cleaning_frequency

    # First appointment after signup
    current_date = signup + pd.Timedelta(
        days=int(rng.integers(1, 15))
    )

    # Simulate customer retention duration
    active_months = int(rng.integers(3, 37))
    churn_date = min(
        signup + pd.DateOffset(months=active_months),
        end_date
    )

    if frequency == "One-time":
        max_bookings = 1
    else:
        max_bookings = 200

    customer_bookings = 0

    while (
        current_date <= churn_date
        and customer_bookings < max_bookings
    ):

        # Select cleaning service
        if frequency == "One-time":
            service_id = int(
                rng.choice([301, 302, 303])
            )
        else:
            service_id = int(
                rng.choice(
                    [301, 302, 303, 304],
                    p=[0.30, 0.10, 0.05, 0.55]
                )
            )

        # Generate appointment status
        status = rng.choice(
            ["Completed", "Cancelled"],
            p=[0.92, 0.08]
        )

        price = round(
            service_prices[service_id]
            * rng.uniform(0.90, 1.25),
            2
        )

        if status == "Cancelled":
            price = 0

        booking_records.append({
            "booking_id": booking_id,
            "customer_id": customer.customer_id,
            "service_id": service_id,
            "booking_date": current_date,
            "status": status,
            "price": price
        })

        booking_id += 1
        customer_bookings += 1

        if frequency == "One-time":
            break

        # Advance to next scheduled cleaning
        interval = frequency_days[frequency]

        # Allow slight scheduling variation
        variation = int(rng.integers(-2, 3))

        current_date += pd.Timedelta(
            days=max(1, interval + variation)
        )

bookings = pd.DataFrame(booking_records)

bookings.to_csv(
    DATA_DIR / "bookings.csv",
    index=False
)

print("\nRealistic bookings created successfully!")
print(f"Total bookings: {len(bookings):,}")
print(bookings.head())



# ---------------------------------
# JOB ASSIGNMENTS & LABOR COSTS
# ---------------------------------

assignments = []

assignment_id = 50001

# Look up employee wages and service hours
employee_wages = employees.set_index(
    "employee_id"
)["hourly_wage"].to_dict()

service_hours = services.set_index(
    "service_id"
)["estimated_hours"].to_dict()

# Only completed bookings receive assignments
completed_bookings = bookings[
    bookings["status"] == "Completed"
]

for booking in completed_bookings.itertuples(index=False):

    # Assign one or two employees per job
    team_size = int(
        rng.choice([1, 2], p=[0.35, 0.65])
    )

    assigned_employees = rng.choice(
        employees["employee_id"],
        size=team_size,
        replace=False
    )

    # Total estimated labor hours for the job
    total_hours = (
        service_hours[booking.service_id]
        * rng.uniform(0.85, 1.25)
    )

    # Split hours across the assigned employees
    hours_per_employee = total_hours / team_size

    for employee_id in assigned_employees:

        hourly_wage = employee_wages[employee_id]

        assignments.append({
            "assignment_id": assignment_id,
            "booking_id": booking.booking_id,
            "employee_id": int(employee_id),
            "hours_worked": round(
                hours_per_employee, 2
            ),
            "hourly_wage": hourly_wage,
            "labor_cost": round(
                hours_per_employee * hourly_wage, 2
            )
        })

        assignment_id += 1

job_assignments = pd.DataFrame(assignments)

job_assignments.to_csv(
    DATA_DIR / "job_assignments.csv",
    index=False
)

print("\nJob assignments created successfully!")
print(f"Total assignments: {len(job_assignments)}")
print(job_assignments.head())


# ---------------------------------
# OPERATING EXPENSES DATASET
# ---------------------------------

expense_categories = {
    "Cleaning Supplies": (150, 500),
    "Transportation": (300, 900),
    "Insurance": (200, 450),
    "Marketing": (250, 800),
    "Administration": (150, 400),
    "Equipment": (100, 600)
}

expense_records = []
expense_id = 60001

# Generate monthly operating expenses
months = pd.date_range(
    start="2023-01-01",
    end="2025-12-01",
    freq="MS"
)

for month in months:
    for category, (min_cost, max_cost) in expense_categories.items():

        amount = round(
            rng.uniform(min_cost, max_cost), 2
        )

        expense_records.append({
            "expense_id": expense_id,
            "expense_date": month,
            "category": category,
            "amount": amount
        })

        expense_id += 1

expenses = pd.DataFrame(expense_records)

expenses.to_csv(
    DATA_DIR / "expenses.csv",
    index=False
)

print("\nOperating expenses created successfully!")
print(f"Total expense records: {len(expenses)}")
print(expenses.head())

print("\nTotal operating expenses: $"
      f"{expenses['amount'].sum():,.2f}")


# ---------------------------------
# DATA QUALITY CORRECTIONS
# ---------------------------------

# Ensure customer signup dates are not after
# their earliest cleaning appointment

first_bookings = (
    bookings.groupby("customer_id")["booking_date"]
    .min()
)

customers["signup_date"] = customers.apply(
    lambda row: min(
        row["signup_date"],
        first_bookings.get(
            row["customer_id"],
            row["signup_date"]
        )
    ),
    axis=1
)

# Ensure employee hire dates are not after
# their earliest assigned cleaning appointment

employee_first_jobs = (
    job_assignments
    .merge(
        bookings[["booking_id", "booking_date"]],
        on="booking_id"
    )
    .groupby("employee_id")["booking_date"]
    .min()
)

employees["hire_date"] = employees.apply(
    lambda row: min(
        row["hire_date"],
        employee_first_jobs.get(
            row["employee_id"],
            row["hire_date"]
        )
    ),
    axis=1
)

# Save corrected customer and employee tables
customers.to_csv(
    DATA_DIR / "customers.csv",
    index=False
)

employees.to_csv(
    DATA_DIR / "employees.csv",
    index=False
)

print("\nCustomer and employee dates corrected!")


