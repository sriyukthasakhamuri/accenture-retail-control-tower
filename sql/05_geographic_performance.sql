-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- GEOGRAPHIC PERFORMANCE ANALYSIS
--
-- Reporting grain:
-- One row = one customer state
-- =========================================================


-- ---------------------------------------------------------
-- 1. AGGREGATE ORDER ITEMS TO ORDER GRAIN
-- ---------------------------------------------------------

WITH item_by_order AS (

    SELECT
        order_id,

        SUM(price)
            AS merchandise_value,

        SUM(freight_value)
            AS freight_value,

        SUM(item_total_value)
            AS item_value_including_freight,

        COUNT(*)
            AS items_sold

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

        SUM(payment_value)
            AS payment_value

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

        AVG(review_score)
            AS average_review_score

    FROM fact_reviews

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 4. CREATE ONE ANALYTICAL ROW PER ORDER
-- ---------------------------------------------------------

order_geography AS (

    SELECT
        o.order_id,

        o.customer_id,

        c.customer_unique_id,

        c.customer_zip_code_prefix,

        COALESCE(
            g.state,
            c.customer_state,
            'Unknown'
        ) AS customer_state,

        g.latitude,

        g.longitude,

        CASE
            WHEN
                g.latitude IS NOT NULL
                AND g.longitude IS NOT NULL
            THEN 1
            ELSE 0
        END AS has_geography,

        o.is_delivered,

        o.is_late_delivery,

        o.delivery_time_days,

        o.delivery_delay_days,

        i.items_sold,

        i.merchandise_value,

        i.freight_value,

        i.item_value_including_freight,

        p.payment_value,

        r.average_review_score

    FROM fact_orders AS o

    LEFT JOIN dim_customer AS c
        ON o.customer_id = c.customer_id

    LEFT JOIN dim_geography AS g
        ON CAST(
            c.customer_zip_code_prefix
            AS VARCHAR
        ) = CAST(
            g.zip_code_prefix
            AS VARCHAR
        )

    LEFT JOIN item_by_order AS i
        ON o.order_id = i.order_id

    LEFT JOIN payment_by_order AS p
        ON o.order_id = p.order_id

    LEFT JOIN review_by_order AS r
        ON o.order_id = r.order_id
),


-- ---------------------------------------------------------
-- 5. CALCULATE STATE-LEVEL KPIS
-- ---------------------------------------------------------

state_metrics AS (

    SELECT
        customer_state,

        COUNT(
            DISTINCT order_id
        ) AS orders,

        COUNT(
            DISTINCT customer_unique_id
        ) AS unique_customers,

        SUM(
            COALESCE(
                items_sold,
                0
            )
        ) AS items_sold,

        SUM(
            CASE
                WHEN is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

        ROUND(
            SUM(
                merchandise_value
            ),
            2
        ) AS merchandise_value,

        ROUND(
            SUM(
                freight_value
            ),
            2
        ) AS freight_value,

        ROUND(
            SUM(
                item_value_including_freight
            ),
            2
        ) AS item_value_including_freight,

        ROUND(
            SUM(
                payment_value
            ),
            2
        ) AS payment_value,

        ROUND(
            AVG(
                payment_value
            ),
            2
        ) AS average_order_value,

        ROUND(
            100.0
            *
            SUM(
                freight_value
            )
            /
            NULLIF(
                SUM(
                    item_value_including_freight
                ),
                0
            ),
            2
        ) AS freight_share_pct,

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
        ) AS negative_review_rate_pct,

        ROUND(
            100.0
            *
            AVG(
                has_geography
            ),
            2
        ) AS geography_coverage_pct,

        ROUND(
            AVG(
                latitude
            ),
            6
        ) AS average_customer_latitude,

        ROUND(
            AVG(
                longitude
            ),
            6
        ) AS average_customer_longitude

    FROM order_geography

    GROUP BY
        customer_state
),


-- ---------------------------------------------------------
-- 6. ADD STATE PERFORMANCE RANKINGS
-- ---------------------------------------------------------

state_ranked AS (

    SELECT
        *,

        DENSE_RANK() OVER (
            ORDER BY
                merchandise_value DESC
        ) AS revenue_rank,

        DENSE_RANK() OVER (
            ORDER BY
                orders DESC
        ) AS order_volume_rank,

        DENSE_RANK() OVER (
            ORDER BY
                late_delivery_rate_pct DESC
        ) AS late_delivery_risk_rank

    FROM state_metrics
)


-- ---------------------------------------------------------
-- 7. FINAL GEOGRAPHIC REPORT
-- ---------------------------------------------------------

SELECT
    customer_state,

    revenue_rank,

    order_volume_rank,

    late_delivery_risk_rank,

    orders,

    unique_customers,

    items_sold,

    delivered_orders,

    merchandise_value,

    freight_value,

    item_value_including_freight,

    payment_value,

    average_order_value,

    freight_share_pct,

    average_delivery_time_days,

    late_delivery_rate_pct,

    average_review_score,

    positive_review_rate_pct,

    negative_review_rate_pct,

    geography_coverage_pct,

    average_customer_latitude,

    average_customer_longitude

FROM state_ranked

ORDER BY
    merchandise_value DESC;