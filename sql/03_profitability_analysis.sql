
-- ============================================
-- MONTHLY REVENUE, LABOR, AND EXPENSE ANALYSIS
-- ============================================

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', booking_date) AS month,
        SUM(price) AS revenue
    FROM bookings
    WHERE status = 'Completed'
    GROUP BY strftime('%Y-%m', booking_date)
),

monthly_labor AS (
    SELECT
        strftime('%Y-%m', b.booking_date) AS month,
        SUM(ja.labor_cost) AS labor_cost
    FROM job_assignments ja
    JOIN bookings b
        ON ja.booking_id = b.booking_id
    WHERE b.status = 'Completed'
    GROUP BY strftime('%Y-%m', b.booking_date)
),

monthly_expenses AS (
    SELECT
        strftime('%Y-%m', expense_date) AS month,
        SUM(amount) AS operating_expenses
    FROM expenses
    GROUP BY strftime('%Y-%m', expense_date)
)

SELECT
    r.month,

    ROUND(r.revenue, 2) AS revenue,

    ROUND(COALESCE(l.labor_cost, 0), 2) AS labor_cost,

    ROUND(COALESCE(e.operating_expenses, 0), 2)
        AS operating_expenses,

    ROUND(
        r.revenue
        - COALESCE(l.labor_cost, 0)
        - COALESCE(e.operating_expenses, 0),
        2
    ) AS estimated_operating_profit,

    ROUND(
        100.0 *
        (
            r.revenue
            - COALESCE(l.labor_cost, 0)
            - COALESCE(e.operating_expenses, 0)
        ) / NULLIF(r.revenue, 0),
        2
    ) AS estimated_operating_margin_pct

FROM monthly_revenue r

LEFT JOIN monthly_labor l
    ON r.month = l.month

LEFT JOIN monthly_expenses e
    ON r.month = e.month

ORDER BY r.month;


-- ============================================
-- ANNUAL PROFITABILITY SUMMARY
-- ============================================

WITH annual_revenue AS (
    SELECT
        strftime('%Y', booking_date) AS year,
        SUM(price) AS revenue
    FROM bookings
    WHERE status = 'Completed'
    GROUP BY strftime('%Y', booking_date)
),

annual_labor AS (
    SELECT
        strftime('%Y', b.booking_date) AS year,
        SUM(ja.labor_cost) AS labor_cost
    FROM job_assignments ja
    JOIN bookings b
        ON ja.booking_id = b.booking_id
    WHERE b.status = 'Completed'
    GROUP BY strftime('%Y', b.booking_date)
),

annual_expenses AS (
    SELECT
        strftime('%Y', expense_date) AS year,
        SUM(amount) AS operating_expenses
    FROM expenses
    GROUP BY strftime('%Y', expense_date)
)

SELECT
    r.year,

    ROUND(r.revenue, 2) AS revenue,

    ROUND(COALESCE(l.labor_cost, 0), 2)
        AS labor_cost,

    ROUND(COALESCE(e.operating_expenses, 0), 2)
        AS operating_expenses,

    ROUND(
        r.revenue
        - COALESCE(l.labor_cost, 0)
        - COALESCE(e.operating_expenses, 0),
        2
    ) AS estimated_profit,

    ROUND(
        100.0 *
        (
            r.revenue
            - COALESCE(l.labor_cost, 0)
            - COALESCE(e.operating_expenses, 0)
        ) / NULLIF(r.revenue, 0),
        2
    ) AS estimated_profit_margin_pct

FROM annual_revenue r

LEFT JOIN annual_labor l
    ON r.year = l.year

LEFT JOIN annual_expenses e
    ON r.year = e.year

ORDER BY r.year;
