-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- DELIVERY & OPERATIONS PERFORMANCE
--
-- Reporting grain:
-- One row = one delivery performance segment
-- =========================================================


-- ---------------------------------------------------------
-- 1. AGGREGATE REVIEWS TO ORDER GRAIN
-- ---------------------------------------------------------

WITH review_by_order AS (

    SELECT
        order_id,
        AVG(review_score) AS average_review_score

    FROM fact_reviews

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 2. CREATE ORDER-LEVEL DELIVERY DATASET
-- ---------------------------------------------------------

delivery_orders AS (

    SELECT
        o.order_id,
        o.order_status,
        o.is_delivered,
        o.is_late_delivery,
        o.delivery_time_days,
        o.delivery_delay_days,
        r.average_review_score,

        CASE
            WHEN o.is_delivered != 1
                THEN 'Not Delivered'

            WHEN o.delivery_delay_days IS NULL
                THEN 'Delivery Date Missing'

            WHEN o.is_late_delivery = 1
                THEN 'Late'

            ELSE 'On Time / Early'
        END AS delivery_status

    FROM fact_orders AS o

    LEFT JOIN review_by_order AS r
        ON o.order_id = r.order_id
),


-- ---------------------------------------------------------
-- 3. CALCULATE DELIVERY SEGMENT METRICS
-- ---------------------------------------------------------

delivery_metrics AS (

    SELECT
        delivery_status,

        COUNT(*) AS orders,

        SUM(
            CASE
                WHEN average_review_score IS NOT NULL
                THEN 1
                ELSE 0
            END
        ) AS reviewed_orders,

        ROUND(
            AVG(delivery_time_days),
            2
        ) AS average_delivery_time_days,

        ROUND(
            AVG(delivery_delay_days),
            2
        ) AS average_delivery_delay_days,

        ROUND(
            AVG(average_review_score),
            2
        ) AS average_review_score,

        ROUND(
            100.0 * AVG(
                CASE
                    WHEN average_review_score >= 4
                        THEN 1.0

                    WHEN average_review_score IS NOT NULL
                        THEN 0.0

                    ELSE NULL
                END
            ),
            2
        ) AS positive_review_rate_pct,

        ROUND(
            100.0 * AVG(
                CASE
                    WHEN average_review_score <= 2
                        THEN 1.0

                    WHEN average_review_score IS NOT NULL
                        THEN 0.0

                    ELSE NULL
                END
            ),
            2
        ) AS negative_review_rate_pct

    FROM delivery_orders

    GROUP BY
        delivery_status
),


-- ---------------------------------------------------------
-- 4. CALCULATE TOTAL ORDER COUNT
-- ---------------------------------------------------------

order_totals AS (

    SELECT
        COUNT(*) AS all_orders

    FROM delivery_orders
),


-- ---------------------------------------------------------
-- 5. ADD ORDER SHARE
-- ---------------------------------------------------------

delivery_enriched AS (

    SELECT
        d.delivery_status,
        d.orders,

        ROUND(
            100.0 * d.orders
            / NULLIF(t.all_orders, 0),
            2
        ) AS order_share_pct,

        d.reviewed_orders,
        d.average_delivery_time_days,
        d.average_delivery_delay_days,
        d.average_review_score,
        d.positive_review_rate_pct,
        d.negative_review_rate_pct

    FROM delivery_metrics AS d

    CROSS JOIN order_totals AS t
)


-- ---------------------------------------------------------
-- 6. FINAL DELIVERY PERFORMANCE REPORT
-- ---------------------------------------------------------

SELECT
    delivery_status,
    orders,
    order_share_pct,
    reviewed_orders,
    average_delivery_time_days,
    average_delivery_delay_days,
    average_review_score,
    positive_review_rate_pct,
    negative_review_rate_pct

FROM delivery_enriched

ORDER BY
    CASE delivery_status
        WHEN 'On Time / Early' THEN 1
        WHEN 'Late' THEN 2
        WHEN 'Delivery Date Missing' THEN 3
        WHEN 'Not Delivered' THEN 4
        ELSE 5
    END;