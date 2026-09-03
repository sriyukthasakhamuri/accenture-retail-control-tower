-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- CUSTOMER BEHAVIOR ANALYSIS
--
-- Reporting grain:
-- One row = one unique customer
-- =========================================================


-- ---------------------------------------------------------
-- 1. AGGREGATE PAYMENTS TO ORDER GRAIN
-- ---------------------------------------------------------

WITH payment_by_order AS (

    SELECT
        order_id,

        SUM(payment_value)
            AS payment_value

    FROM fact_payments

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 2. AGGREGATE ORDER ITEMS TO ORDER GRAIN
-- ---------------------------------------------------------

item_by_order AS (

    SELECT
        order_id,

        COUNT(*)
            AS items_purchased,

        SUM(price)
            AS merchandise_value,

        SUM(freight_value)
            AS freight_value

    FROM fact_order_items

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 3. AGGREGATE REVIEWS TO ORDER GRAIN
-- ---------------------------------------------------------

review_by_order AS (

    SELECT
        order_id,

        AVG(review_score)
            AS average_review_score

    FROM fact_reviews

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 4. CREATE ONE ANALYTICAL ROW PER ORDER
-- ---------------------------------------------------------

customer_orders AS (

    SELECT
        c.customer_unique_id,

        o.order_id,

        CAST(
            o.order_purchase_timestamp
            AS TIMESTAMP
        ) AS order_purchase_timestamp,

        o.is_delivered,

        o.is_late_delivery,

        o.delivery_time_days,

        o.delivery_delay_days,

        COALESCE(
            p.payment_value,
            0
        ) AS payment_value,

        COALESCE(
            i.items_purchased,
            0
        ) AS items_purchased,

        COALESCE(
            i.merchandise_value,
            0
        ) AS merchandise_value,

        COALESCE(
            i.freight_value,
            0
        ) AS freight_value,

        r.average_review_score

    FROM fact_orders AS o

    INNER JOIN dim_customer AS c
        ON o.customer_id = c.customer_id

    LEFT JOIN payment_by_order AS p
        ON o.order_id = p.order_id

    LEFT JOIN item_by_order AS i
        ON o.order_id = i.order_id

    LEFT JOIN review_by_order AS r
        ON o.order_id = r.order_id
),


-- ---------------------------------------------------------
-- 5. CALCULATE CUSTOMER-LEVEL KPIS
-- ---------------------------------------------------------

customer_metrics AS (

    SELECT
        customer_unique_id,

        COUNT(
            DISTINCT order_id
        ) AS lifetime_orders,

        MIN(
            order_purchase_timestamp
        ) AS first_order_timestamp,

        MAX(
            order_purchase_timestamp
        ) AS latest_order_timestamp,

        SUM(
            items_purchased
        ) AS lifetime_items_purchased,

        ROUND(
            SUM(
                merchandise_value
            ),
            2
        ) AS lifetime_merchandise_value,

        ROUND(
            SUM(
                freight_value
            ),
            2
        ) AS lifetime_freight_value,

        ROUND(
            SUM(
                payment_value
            ),
            2
        ) AS lifetime_payment_value,

        ROUND(
            AVG(
                payment_value
            ),
            2
        ) AS average_order_value,

        SUM(
            CASE
                WHEN is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

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
            AVG(
                average_review_score
            ),
            2
        ) AS average_review_score

    FROM customer_orders

    GROUP BY
        customer_unique_id
),


-- ---------------------------------------------------------
-- 6. ADD CUSTOMER BEHAVIOR FLAGS
-- ---------------------------------------------------------

customer_behavior AS (

    SELECT
        *,

        CASE
            WHEN lifetime_orders = 1
                THEN 'One-Time Customer'

            ELSE 'Repeat Customer'
        END AS customer_type,

        CASE
            WHEN lifetime_orders = 1
                THEN '1 Order'

            WHEN lifetime_orders BETWEEN 2 AND 3
                THEN '2-3 Orders'

            WHEN lifetime_orders BETWEEN 4 AND 5
                THEN '4-5 Orders'

            ELSE '6+ Orders'
        END AS order_frequency_segment,

        DATE_DIFF(
            'day',
            CAST(first_order_timestamp AS DATE),
            CAST(latest_order_timestamp AS DATE)
        ) AS customer_lifetime_days

    FROM customer_metrics
),


-- ---------------------------------------------------------
-- 7. ADD CUSTOMER VALUE RANK
-- ---------------------------------------------------------

customer_ranked AS (

    SELECT
        *,

        DENSE_RANK() OVER (
            ORDER BY
                lifetime_payment_value DESC
        ) AS customer_value_rank

    FROM customer_behavior
)


-- ---------------------------------------------------------
-- 8. FINAL CUSTOMER REPORT
-- ---------------------------------------------------------

SELECT
    customer_unique_id,

    customer_value_rank,

    customer_type,

    order_frequency_segment,

    lifetime_orders,

    first_order_timestamp,

    latest_order_timestamp,

    customer_lifetime_days,

    lifetime_items_purchased,

    lifetime_merchandise_value,

    lifetime_freight_value,

    lifetime_payment_value,

    average_order_value,

    delivered_orders,

    average_delivery_time_days,

    late_delivery_rate_pct,

    average_review_score

FROM customer_ranked

ORDER BY
    lifetime_payment_value DESC;