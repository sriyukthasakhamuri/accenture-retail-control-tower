-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- EXECUTIVE KPI SUMMARY
-- =========================================================

WITH order_metrics AS (

    SELECT
        COUNT(*) AS total_orders,

        SUM(
            CASE
                WHEN is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

        COUNT(
            DISTINCT customer_id
        ) AS customer_records

    FROM fact_orders
),

customer_metrics AS (

    SELECT
        COUNT(
            DISTINCT customer_unique_id
        ) AS unique_customers

    FROM dim_customer
),

item_metrics AS (

    SELECT
        SUM(price) AS merchandise_value,

        SUM(freight_value) AS freight_value,

        SUM(item_total_value)
            AS item_value_including_freight,

        COUNT(*) AS order_item_rows,

        COUNT(
            DISTINCT seller_id
        ) AS active_sellers

    FROM fact_order_items
),

payment_by_order AS (

    SELECT
        order_id,

        SUM(payment_value)
            AS order_payment_value

    FROM fact_payments

    GROUP BY
        order_id
),

payment_metrics AS (

    SELECT
        SUM(order_payment_value)
            AS total_payment_value,

        AVG(order_payment_value)
            AS average_order_value,

        COUNT(*)
            AS paid_orders

    FROM payment_by_order
),

delivery_metrics AS (

    SELECT
        COUNT(*) AS delivered_orders_with_dates,

        AVG(delivery_time_days)
            AS average_delivery_time_days,

        100.0
        *
        AVG(
            CASE
                WHEN is_late_delivery = 1
                THEN 1.0
                ELSE 0.0
            END
        ) AS late_delivery_rate_pct

    FROM fact_orders

    WHERE
        is_delivered = 1
        AND delivery_delay_days IS NOT NULL
),

review_by_order AS (

    SELECT
        order_id,

        AVG(review_score)
            AS average_order_review_score

    FROM fact_reviews

    GROUP BY
        order_id
),

review_metrics AS (

    SELECT
        COUNT(*) AS reviewed_orders,

        AVG(average_order_review_score)
            AS average_review_score,

        100.0
        *
        AVG(
            CASE
                WHEN average_order_review_score >= 4
                THEN 1.0
                ELSE 0.0
            END
        ) AS positive_review_rate_pct,

        100.0
        *
        AVG(
            CASE
                WHEN average_order_review_score <= 2
                THEN 1.0
                ELSE 0.0
            END
        ) AS negative_review_rate_pct

    FROM review_by_order
)

SELECT
    o.total_orders,

    o.delivered_orders,

    c.unique_customers,

    i.active_sellers,

    ROUND(
        i.merchandise_value,
        2
    ) AS merchandise_value,

    ROUND(
        i.freight_value,
        2
    ) AS freight_value,

    ROUND(
        i.item_value_including_freight,
        2
    ) AS item_value_including_freight,

    ROUND(
        p.total_payment_value,
        2
    ) AS total_payment_value,

    ROUND(
        p.average_order_value,
        2
    ) AS average_order_value,

    ROUND(
        d.average_delivery_time_days,
        2
    ) AS average_delivery_time_days,

    ROUND(
        d.late_delivery_rate_pct,
        2
    ) AS late_delivery_rate_pct,

    ROUND(
        r.average_review_score,
        2
    ) AS average_review_score,

    ROUND(
        r.positive_review_rate_pct,
        2
    ) AS positive_review_rate_pct,

    ROUND(
        r.negative_review_rate_pct,
        2
    ) AS negative_review_rate_pct

FROM order_metrics AS o

CROSS JOIN customer_metrics AS c
CROSS JOIN item_metrics AS i
CROSS JOIN payment_metrics AS p
CROSS JOIN delivery_metrics AS d
CROSS JOIN review_metrics AS r;