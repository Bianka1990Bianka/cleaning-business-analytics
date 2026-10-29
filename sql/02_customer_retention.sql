
-- ============================================
-- CUSTOMER RETENTION COHORT ANALYSIS
-- ============================================

WITH first_booking AS (
    SELECT
        customer_id,
        MIN(date(booking_date, 'start of month')) AS cohort_month
    FROM bookings
    WHERE status = 'Completed'
    GROUP BY customer_id
),

customer_activity AS (
    SELECT DISTINCT
        b.customer_id,
        f.cohort_month,
        date(b.booking_date, 'start of month') AS activity_month
    FROM bookings b
    JOIN first_booking f
        ON b.customer_id = f.customer_id
    WHERE b.status = 'Completed'
),

cohort_activity AS (
    SELECT
        customer_id,
        cohort_month,
        (
            (CAST(strftime('%Y', activity_month) AS INTEGER) -
             CAST(strftime('%Y', cohort_month) AS INTEGER)) * 12
            +
            (CAST(strftime('%m', activity_month) AS INTEGER) -
             CAST(strftime('%m', cohort_month) AS INTEGER))
        ) AS months_since_first_booking
    FROM customer_activity
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM first_booking
    GROUP BY cohort_month
)

SELECT
    ca.cohort_month,
    ca.months_since_first_booking,
    cs.cohort_size,
    COUNT(DISTINCT ca.customer_id) AS active_customers,
    ROUND(
        100.0 * COUNT(DISTINCT ca.customer_id)
        / NULLIF(cs.cohort_size, 0),
        2
    ) AS retention_pct

FROM cohort_activity ca

JOIN cohort_sizes cs
    ON ca.cohort_month = cs.cohort_month

GROUP BY
    ca.cohort_month,
    ca.months_since_first_booking,
    cs.cohort_size

ORDER BY
    ca.cohort_month,
    ca.months_since_first_booking;


;

-- ============================================
-- CUSTOMER INACTIVITY ANALYSIS
-- ============================================

WITH last_booking AS (
    SELECT
        c.customer_id,
        c.cleaning_frequency,
        MAX(
            CASE
                WHEN b.status = 'Completed'
                THEN date(b.booking_date)
            END
        ) AS last_booking_date
    FROM customers c
    LEFT JOIN bookings b
        ON c.customer_id = b.customer_id
    GROUP BY
        c.customer_id,
        c.cleaning_frequency
),

customer_status AS (
    SELECT
        customer_id,
        cleaning_frequency,
        last_booking_date,
        CASE
            WHEN last_booking_date IS NULL
                THEN 'Never Completed'
            WHEN julianday('2025-12-31') -
                 julianday(last_booking_date) > 90
                THEN 'Inactive'
            ELSE 'Active'
        END AS activity_status
    FROM last_booking
)

SELECT
    cleaning_frequency,
    activity_status,
    COUNT(*) AS customers
FROM customer_status
GROUP BY
    cleaning_frequency,
    activity_status
ORDER BY
    cleaning_frequency,
    activity_status;


-- ============================================
-- RECURRING CUSTOMER REACTIVATION OPPORTUNITY
-- ============================================

WITH customer_summary AS (
    SELECT
        c.customer_id,
        c.cleaning_frequency,
        COUNT(b.booking_id) AS completed_jobs,
        COALESCE(SUM(b.price), 0) AS lifetime_revenue,
        MAX(date(b.booking_date)) AS last_booking_date
    FROM customers c
    LEFT JOIN bookings b
        ON c.customer_id = b.customer_id
        AND b.status = 'Completed'
    WHERE c.cleaning_frequency IN ('Weekly', 'Biweekly')
    GROUP BY
        c.customer_id,
        c.cleaning_frequency
),

inactive_customers AS (
    SELECT
        *,
        ROUND(
            julianday('2025-12-31') -
            julianday(last_booking_date),
            0
        ) AS days_inactive
    FROM customer_summary
    WHERE last_booking_date IS NOT NULL
      AND julianday('2025-12-31') -
          julianday(last_booking_date) > 90
)

SELECT
    cleaning_frequency,
    COUNT(*) AS inactive_customers,
    SUM(completed_jobs) AS historical_jobs,
    ROUND(SUM(lifetime_revenue), 2) AS historical_revenue,
    ROUND(AVG(lifetime_revenue), 2) AS avg_historical_revenue,
    ROUND(AVG(days_inactive), 0) AS avg_days_inactive
FROM inactive_customers
GROUP BY cleaning_frequency
ORDER BY historical_revenue DESC;
