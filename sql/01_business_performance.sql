
-- ============================================
-- RESIDENTIAL CLEANING BUSINESS ANALYTICS
-- 01: CORE BUSINESS PERFORMANCE
-- ============================================

-- 1. TOTAL REVENUE
SELECT
    ROUND(SUM(price), 2) AS total_revenue
FROM bookings
WHERE status = 'Completed';


-- 2. COMPLETED CLEANING JOBS
SELECT
    COUNT(*) AS completed_jobs
FROM bookings
WHERE status = 'Completed';


-- 3. AVERAGE JOB VALUE
SELECT
    ROUND(AVG(price), 2) AS average_job_value
FROM bookings
WHERE status = 'Completed';


-- 4. CANCELLATION RATE
SELECT
    COUNT(*) AS total_bookings,
    SUM(
        CASE
            WHEN status = 'Cancelled' THEN 1
            ELSE 0
        END
    ) AS cancelled_bookings,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN status = 'Cancelled' THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_rate_pct
FROM bookings;


-- 5. TOTAL DIRECT LABOR COST

-- ============================================
-- 6. PROFITABILITY BY CLEANING SERVICE
-- ============================================

WITH labor_by_booking AS (
    SELECT
        booking_id,
        SUM(labor_cost) AS labor_cost
    FROM job_assignments
    GROUP BY booking_id
)

SELECT
    s.service_name,

    COUNT(b.booking_id) AS completed_jobs,

    ROUND(SUM(b.price), 2) AS total_revenue,

    ROUND(
        AVG(b.price), 2
    ) AS average_job_value,

    ROUND(
        SUM(COALESCE(l.labor_cost, 0)), 2
    ) AS total_labor_cost,

    ROUND(
        SUM(b.price) -
        SUM(COALESCE(l.labor_cost, 0)), 2
    ) AS contribution_after_labor,

    ROUND(
        100.0 *
        (
            SUM(b.price) -
            SUM(COALESCE(l.labor_cost, 0))
        ) / NULLIF(SUM(b.price), 0),
        2
    ) AS contribution_margin_pct

FROM bookings b

JOIN services s
    ON b.service_id = s.service_id

LEFT JOIN labor_by_booking l
    ON b.booking_id = l.booking_id

WHERE b.status = 'Completed'

GROUP BY s.service_name

ORDER BY contribution_after_labor DESC;


-- ============================================
-- 7. MONTHLY REVENUE AND GROWTH
-- ============================================

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', booking_date) AS month,
        ROUND(SUM(price), 2) AS revenue,
        COUNT(*) AS completed_jobs
    FROM bookings
    WHERE status = 'Completed'
    GROUP BY strftime('%Y-%m', booking_date)
),

revenue_growth AS (
    SELECT
        month,
        revenue,
        completed_jobs,
        LAG(revenue) OVER (
            ORDER BY month
        ) AS previous_month_revenue
    FROM monthly_revenue
)

SELECT
    month,
    revenue,
    completed_jobs,
    ROUND(
        100.0 *
        (revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        2
    ) AS mom_growth_pct
FROM revenue_growth
ORDER BY month;


-- ============================================
-- 8. YEARLY REVENUE AND YOY GROWTH
-- ============================================

WITH yearly_revenue AS (
    SELECT
        strftime('%Y', booking_date) AS year,
        COUNT(*) AS completed_jobs,
        ROUND(SUM(price), 2) AS revenue
    FROM bookings
    WHERE status = 'Completed'
    GROUP BY strftime('%Y', booking_date)
),

growth AS (
    SELECT
        year,
        completed_jobs,
        revenue,
        LAG(revenue) OVER (
            ORDER BY year
        ) AS previous_year_revenue
    FROM yearly_revenue
)

SELECT
    year,
    completed_jobs,
    revenue,
    ROUND(
        100.0 *
        (revenue - previous_year_revenue)
        / NULLIF(previous_year_revenue, 0),
        2
    ) AS yoy_growth_pct
FROM growth
ORDER BY year;


-- ============================================
-- 9. CUSTOMER VALUE BY CLEANING FREQUENCY
-- ============================================

WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.cleaning_frequency,
        COUNT(b.booking_id) AS completed_jobs,
        COALESCE(SUM(b.price), 0) AS total_revenue
    FROM customers c

    LEFT JOIN bookings b
        ON c.customer_id = b.customer_id
        AND b.status = 'Completed'

    GROUP BY
        c.customer_id,
        c.cleaning_frequency
)

SELECT
    cleaning_frequency,

    COUNT(*) AS total_customers,

    SUM(completed_jobs) AS completed_jobs,

    ROUND(
        AVG(completed_jobs), 2
    ) AS avg_jobs_per_customer,

    ROUND(
        SUM(total_revenue), 2
    ) AS total_revenue,

    ROUND(
        AVG(total_revenue), 2
    ) AS avg_customer_revenue

FROM customer_revenue

GROUP BY cleaning_frequency

ORDER BY avg_customer_revenue DESC;


-- ============================================
-- 10. CUSTOMER REPEAT BOOKING ANALYSIS
-- ============================================

WITH customer_activity AS (
    SELECT
        c.customer_id,
        COUNT(b.booking_id) AS completed_jobs,
        COALESCE(SUM(b.price), 0) AS revenue
    FROM customers c
    LEFT JOIN bookings b
        ON c.customer_id = b.customer_id
        AND b.status = 'Completed'
    GROUP BY c.customer_id
)

SELECT
    COUNT(*) AS total_customers,

    SUM(
        CASE WHEN completed_jobs = 0
        THEN 1 ELSE 0 END
    ) AS customers_without_completed_jobs,

    SUM(
        CASE WHEN completed_jobs = 1
        THEN 1 ELSE 0 END
    ) AS one_time_customers,

    SUM(
        CASE WHEN completed_jobs >= 2
        THEN 1 ELSE 0 END
    ) AS repeat_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN completed_jobs >= 2
            THEN 1 ELSE 0 END)
        / NULLIF(
            SUM(CASE WHEN completed_jobs >= 1
                THEN 1 ELSE 0 END), 0
        ),
        2
    ) AS repeat_customer_rate_pct

FROM customer_activity;

