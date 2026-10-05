-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- MONTHLY PERFORMANCE ANALYSIS
--
-- Reporting grain:
-- One row = one calendar month
--
-- Design:
-- Uses dim_date as the reporting calendar so months with
-- zero order activity are still represented.
-- =========================================================


-- ---------------------------------------------------------
-- 1. AGGREGATE ORDER ITEMS TO ORDER GRAIN
-- ---------------------------------------------------------

WITH item_by_order AS (

    SELECT
        order_id,

        SUM(price) AS merchandise_value,

        SUM(freight_value) AS freight_value,

        SUM(item_total_value)
            AS item_value_including_freight,

        COUNT(*) AS item_count

    FROM fact_order_items

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 2. AGGREGATE PAYMENTS TO ORDER GRAIN
-- ---------------------------------------------------------

payment_by_order AS (

    SELECT
        order_id,

        SUM(payment_value) AS payment_value,

        COUNT(*) AS payment_record_count

    FROM fact_payments

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 3. AGGREGATE REVIEWS TO ORDER GRAIN
-- ---------------------------------------------------------

review_by_order AS (

    SELECT
        order_id,

        AVG(review_score) AS average_review_score

    FROM fact_reviews

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 4. CREATE ONE ANALYTICAL ROW PER ORDER
-- ---------------------------------------------------------

order_level AS (

    SELECT
        o.order_id,

        o.customer_id,

        c.customer_unique_id,

        o.order_status,

        o.is_delivered,

        o.is_late_delivery,

        o.delivery_time_days,

        o.delivery_delay_days,

        CAST(
            o.order_purchase_timestamp
            AS DATE
        ) AS purchase_date,

        i.merchandise_value,

        i.freight_value,

        i.item_value_including_freight,

        i.item_count,

        p.payment_value,

        p.payment_record_count,

        r.average_review_score

    FROM fact_orders AS o

    LEFT JOIN dim_customer AS c
        ON o.customer_id = c.customer_id

    LEFT JOIN item_by_order AS i
        ON o.order_id = i.order_id

    LEFT JOIN payment_by_order AS p
        ON o.order_id = p.order_id

    LEFT JOIN review_by_order AS r
        ON o.order_id = r.order_id
),


-- ---------------------------------------------------------
-- 5. CONNECT ORDERS TO DATE DIMENSION
-- ---------------------------------------------------------

order_with_calendar AS (

    SELECT
        o.*,

        d.year,

        d.month_number,

        d.month_name,

        d.year_month,

        d.year_month_sort

    FROM order_level AS o

    INNER JOIN dim_date AS d
        ON o.purchase_date = d.date
),


-- ---------------------------------------------------------
-- 6. CALCULATE TRANSACTION-BASED MONTHLY METRICS
-- ---------------------------------------------------------

monthly_metrics AS (

    SELECT
        year_month_sort,

        COUNT(
            DISTINCT order_id
        ) AS total_orders,

        COUNT(
            DISTINCT customer_unique_id
        ) AS unique_customers,

        SUM(
            CASE
                WHEN is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

        ROUND(
            SUM(merchandise_value),
            2
        ) AS merchandise_value,

        ROUND(
            SUM(freight_value),
            2
        ) AS freight_value,

        ROUND(
            SUM(item_value_including_freight),
            2
        ) AS item_value_including_freight,

        ROUND(
            SUM(payment_value),
            2
        ) AS payment_value,

        ROUND(
            AVG(payment_value),
            2
        ) AS average_order_value,

        ROUND(
            AVG(
                CASE
                    WHEN is_delivered = 1
                    THEN delivery_time_days
                END
            ),
            2
        ) AS average_delivery_time_days,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN
                        is_delivered = 1
                        AND delivery_delay_days IS NOT NULL
                    THEN is_late_delivery
                END
            ),
            2
        ) AS late_delivery_rate_pct,

        ROUND(
            AVG(average_review_score),
            2
        ) AS average_review_score,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN average_review_score >= 4
                    THEN 1.0

                    WHEN average_review_score IS NOT NULL
                    THEN 0.0
                END
            ),
            2
        ) AS positive_review_rate_pct,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN average_review_score <= 2
                    THEN 1.0

                    WHEN average_review_score IS NOT NULL
                    THEN 0.0
                END
            ),
            2
        ) AS negative_review_rate_pct

    FROM order_with_calendar

    GROUP BY
        year_month_sort
),


-- ---------------------------------------------------------
-- 7. IDENTIFY ORDER ACTIVITY RANGE
--
-- We use the first and last purchase months rather than
-- the entire dim_date range because dim_date also covers
-- shipping, delivery, and review dates.
-- ---------------------------------------------------------

order_month_range AS (

    SELECT
        MIN(year_month_sort)
            AS first_order_month,

        MAX(year_month_sort)
            AS last_order_month

    FROM order_with_calendar
),


-- ---------------------------------------------------------
-- 8. CREATE CONTINUOUS MONTHLY REPORTING CALENDAR
-- ---------------------------------------------------------

reporting_months AS (

    SELECT
        d.year,

        d.month_number,

        d.month_name,

        d.year_month,

        d.year_month_sort

    FROM dim_date AS d

    CROSS JOIN order_month_range AS r

    WHERE
        d.year_month_sort
            BETWEEN r.first_order_month
            AND r.last_order_month

    GROUP BY
        d.year,
        d.month_number,
        d.month_name,
        d.year_month,
        d.year_month_sort
),


-- ---------------------------------------------------------
-- 9. JOIN MONTHLY ACTIVITY TO COMPLETE CALENDAR
--
-- Additive measures become zero when there was no activity.
-- Rates and averages remain NULL because no observation
-- exists for those measures in a zero-activity month.
-- ---------------------------------------------------------

complete_monthly_metrics AS (

    SELECT
        c.year,

        c.month_number,

        c.month_name,

        c.year_month,

        c.year_month_sort,

        COALESCE(
            m.total_orders,
            0
        ) AS total_orders,

        COALESCE(
            m.unique_customers,
            0
        ) AS unique_customers,

        COALESCE(
            m.delivered_orders,
            0
        ) AS delivered_orders,

        COALESCE(
            m.merchandise_value,
            0
        ) AS merchandise_value,

        COALESCE(
            m.freight_value,
            0
        ) AS freight_value,

        COALESCE(
            m.item_value_including_freight,
            0
        ) AS item_value_including_freight,

        COALESCE(
            m.payment_value,
            0
        ) AS payment_value,

        m.average_order_value,

        m.average_delivery_time_days,

        m.late_delivery_rate_pct,

        m.average_review_score,

        m.positive_review_rate_pct,

        m.negative_review_rate_pct

    FROM reporting_months AS c

    LEFT JOIN monthly_metrics AS m
        ON c.year_month_sort
            = m.year_month_sort
),


-- ---------------------------------------------------------
-- 10. ADD ADVANCED ANALYTICAL SQL METRICS
-- ---------------------------------------------------------

monthly_trends AS (

    SELECT
        *,

        LAG(total_orders) OVER (
            ORDER BY year_month_sort
        ) AS previous_month_orders,

        LAG(payment_value) OVER (
            ORDER BY year_month_sort
        ) AS previous_month_revenue,

        ROUND(
            100.0
            * (
                total_orders
                - LAG(total_orders) OVER (
                    ORDER BY year_month_sort
                )
            )
            /
            NULLIF(
                LAG(total_orders) OVER (
                    ORDER BY year_month_sort
                ),
                0
            ),
            2
        ) AS order_growth_pct,

        ROUND(
            100.0
            * (
                payment_value
                - LAG(payment_value) OVER (
                    ORDER BY year_month_sort
                )
            )
            /
            NULLIF(
                LAG(payment_value) OVER (
                    ORDER BY year_month_sort
                ),
                0
            ),
            2
        ) AS revenue_growth_pct,

        ROUND(
            AVG(payment_value) OVER (
                ORDER BY year_month_sort

                ROWS BETWEEN
                    2 PRECEDING
                    AND CURRENT ROW
            ),
            2
        ) AS revenue_3_month_moving_avg,

        RANK() OVER (
            ORDER BY payment_value DESC
        ) AS revenue_rank

    FROM complete_monthly_metrics
)


-- ---------------------------------------------------------
-- 11. FINAL MONTHLY PERFORMANCE REPORT
-- ---------------------------------------------------------

SELECT
    year_month,

    year,

    month_number,

    month_name,

    total_orders,

    unique_customers,

    delivered_orders,

    merchandise_value,

    freight_value,

    item_value_including_freight,

    payment_value,

    previous_month_orders,

    previous_month_revenue,

    order_growth_pct,

    revenue_growth_pct,

    revenue_3_month_moving_avg,

    revenue_rank,

    average_order_value,

    average_delivery_time_days,

    late_delivery_rate_pct,

    average_review_score,

    positive_review_rate_pct,

    negative_review_rate_pct

FROM monthly_trends

ORDER BY
    year_month_sort;