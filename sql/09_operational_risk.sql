-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- OPERATIONAL RISK PRIORITIZATION
--
-- Purpose:
-- Identify commercially important product categories,
-- sellers, and customer states associated with weaker
-- delivery and customer-review performance.
--
-- Important:
-- These are risk signals / associations.
-- They do not prove that an individual seller, category,
-- or geography caused a delivery or review outcome.
-- =========================================================


-- ---------------------------------------------------------
-- 1. AGGREGATE REVIEWS TO ORDER GRAIN
-- ---------------------------------------------------------

WITH review_by_order AS (

    SELECT
        order_id,

        AVG(
            review_score
        ) AS average_review_score

    FROM fact_reviews

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 2. CALCULATE OVERALL BUSINESS BENCHMARKS
-- ---------------------------------------------------------

overall_benchmarks AS (

    SELECT
        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN
                        o.is_delivered = 1
                        AND o.delivery_delay_days IS NOT NULL
                    THEN o.is_late_delivery
                END
            ),
            2
        ) AS overall_late_delivery_rate_pct,

        ROUND(
            AVG(
                r.average_review_score
            ),
            2
        ) AS overall_average_review_score,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN r.average_review_score <= 2
                    THEN 1.0

                    WHEN r.average_review_score IS NOT NULL
                    THEN 0.0

                    ELSE NULL
                END
            ),
            2
        ) AS overall_negative_review_rate_pct

    FROM fact_orders AS o

    LEFT JOIN review_by_order AS r
        ON o.order_id = r.order_id
),


-- =========================================================
-- PRODUCT CATEGORY RISK
-- =========================================================


-- ---------------------------------------------------------
-- 3. CREATE ORDER + CATEGORY GRAIN
-- ---------------------------------------------------------

category_order AS (

    SELECT
        oi.order_id,

        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS entity_name,

        SUM(
            oi.price
        ) AS merchandise_value

    FROM fact_order_items AS oi

    LEFT JOIN dim_product AS p
        ON oi.product_id = p.product_id

    GROUP BY
        oi.order_id,

        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )
),


-- ---------------------------------------------------------
-- 4. CATEGORY PERFORMANCE
-- ---------------------------------------------------------

category_metrics AS (

    SELECT
        'Product Category'
            AS entity_type,

        c.entity_name,

        COUNT(
            DISTINCT c.order_id
        ) AS orders,

        SUM(
            CASE
                WHEN o.is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

        SUM(
            CASE
                WHEN r.average_review_score IS NOT NULL
                THEN 1
                ELSE 0
            END
        ) AS reviewed_orders,

        ROUND(
            SUM(
                c.merchandise_value
            ),
            2
        ) AS merchandise_value,

        ROUND(
            AVG(
                CASE
                    WHEN o.is_delivered = 1
                    THEN o.delivery_time_days
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
                        o.is_delivered = 1
                        AND o.delivery_delay_days IS NOT NULL
                    THEN o.is_late_delivery
                END
            ),
            2
        ) AS late_delivery_rate_pct,

        ROUND(
            AVG(
                r.average_review_score
            ),
            2
        ) AS average_review_score,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN r.average_review_score <= 2
                    THEN 1.0

                    WHEN r.average_review_score IS NOT NULL
                    THEN 0.0

                    ELSE NULL
                END
            ),
            2
        ) AS negative_review_rate_pct

    FROM category_order AS c

    INNER JOIN fact_orders AS o
        ON c.order_id = o.order_id

    LEFT JOIN review_by_order AS r
        ON c.order_id = r.order_id

    GROUP BY
        c.entity_name
),


-- =========================================================
-- SELLER RISK
-- =========================================================


-- ---------------------------------------------------------
-- 5. CREATE SELLER + ORDER GRAIN
-- ---------------------------------------------------------

seller_order AS (

    SELECT
        seller_id,

        order_id,

        SUM(
            price
        ) AS merchandise_value

    FROM fact_order_items

    GROUP BY
        seller_id,
        order_id
),


-- ---------------------------------------------------------
-- 6. SELLER PERFORMANCE
-- ---------------------------------------------------------

seller_metrics AS (

    SELECT
        'Seller'
            AS entity_type,

        s.seller_id
            AS entity_name,

        COUNT(
            DISTINCT s.order_id
        ) AS orders,

        SUM(
            CASE
                WHEN o.is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

        SUM(
            CASE
                WHEN r.average_review_score IS NOT NULL
                THEN 1
                ELSE 0
            END
        ) AS reviewed_orders,

        ROUND(
            SUM(
                s.merchandise_value
            ),
            2
        ) AS merchandise_value,

        ROUND(
            AVG(
                CASE
                    WHEN o.is_delivered = 1
                    THEN o.delivery_time_days
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
                        o.is_delivered = 1
                        AND o.delivery_delay_days IS NOT NULL
                    THEN o.is_late_delivery
                END
            ),
            2
        ) AS late_delivery_rate_pct,

        ROUND(
            AVG(
                r.average_review_score
            ),
            2
        ) AS average_review_score,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN r.average_review_score <= 2
                    THEN 1.0

                    WHEN r.average_review_score IS NOT NULL
                    THEN 0.0

                    ELSE NULL
                END
            ),
            2
        ) AS negative_review_rate_pct

    FROM seller_order AS s

    INNER JOIN fact_orders AS o
        ON s.order_id = o.order_id

    LEFT JOIN review_by_order AS r
        ON s.order_id = r.order_id

    GROUP BY
        s.seller_id
),


-- =========================================================
-- GEOGRAPHIC RISK
-- =========================================================


-- ---------------------------------------------------------
-- 7. AGGREGATE ITEMS TO ORDER GRAIN
-- ---------------------------------------------------------

item_by_order AS (

    SELECT
        order_id,

        SUM(
            price
        ) AS merchandise_value

    FROM fact_order_items

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 8. STATE PERFORMANCE
-- ---------------------------------------------------------

state_metrics AS (

    SELECT
        'Customer State'
            AS entity_type,

        COALESCE(
            c.customer_state,
            'Unknown'
        ) AS entity_name,

        COUNT(
            DISTINCT o.order_id
        ) AS orders,

        SUM(
            CASE
                WHEN o.is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

        SUM(
            CASE
                WHEN r.average_review_score IS NOT NULL
                THEN 1
                ELSE 0
            END
        ) AS reviewed_orders,

        ROUND(
            SUM(
                i.merchandise_value
            ),
            2
        ) AS merchandise_value,

        ROUND(
            AVG(
                CASE
                    WHEN o.is_delivered = 1
                    THEN o.delivery_time_days
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
                        o.is_delivered = 1
                        AND o.delivery_delay_days IS NOT NULL
                    THEN o.is_late_delivery
                END
            ),
            2
        ) AS late_delivery_rate_pct,

        ROUND(
            AVG(
                r.average_review_score
            ),
            2
        ) AS average_review_score,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN r.average_review_score <= 2
                    THEN 1.0

                    WHEN r.average_review_score IS NOT NULL
                    THEN 0.0

                    ELSE NULL
                END
            ),
            2
        ) AS negative_review_rate_pct

    FROM fact_orders AS o

    INNER JOIN dim_customer AS c
        ON o.customer_id = c.customer_id

    LEFT JOIN item_by_order AS i
        ON o.order_id = i.order_id

    LEFT JOIN review_by_order AS r
        ON o.order_id = r.order_id

    GROUP BY
        COALESCE(
            c.customer_state,
            'Unknown'
        )
),


-- ---------------------------------------------------------
-- 9. COMBINE ALL OPERATIONAL ENTITIES
-- ---------------------------------------------------------

combined_entities AS (

    SELECT * FROM category_metrics

    UNION ALL

    SELECT * FROM seller_metrics

    UNION ALL

    SELECT * FROM state_metrics
),


-- ---------------------------------------------------------
-- 10. ADD OVERALL BENCHMARK COMPARISONS
-- ---------------------------------------------------------

benchmark_comparison AS (

    SELECT
        e.*,

        b.overall_late_delivery_rate_pct,

        b.overall_average_review_score,

        b.overall_negative_review_rate_pct,

        ROUND(
            e.late_delivery_rate_pct
            -
            b.overall_late_delivery_rate_pct,
            2
        ) AS late_delivery_gap_pp,

        ROUND(
            e.average_review_score
            -
            b.overall_average_review_score,
            2
        ) AS review_score_gap,

        ROUND(
            e.negative_review_rate_pct
            -
            b.overall_negative_review_rate_pct,
            2
        ) AS negative_review_gap_pp

    FROM combined_entities AS e

    CROSS JOIN overall_benchmarks AS b
),


-- ---------------------------------------------------------
-- 11. CALCULATE RELATIVE EXPOSURE / RISK PERCENTILES
-- ---------------------------------------------------------

risk_percentiles AS (

    SELECT
        *,

        PERCENT_RANK() OVER (
            PARTITION BY entity_type
            ORDER BY orders
        ) AS order_volume_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY entity_type
            ORDER BY merchandise_value
        ) AS revenue_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY entity_type
            ORDER BY COALESCE(
                late_delivery_rate_pct,
                0
            )
        ) AS late_delivery_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY entity_type
            ORDER BY COALESCE(
                negative_review_rate_pct,
                0
            )
        ) AS negative_review_percentile

    FROM benchmark_comparison
),


-- ---------------------------------------------------------
-- 12. CALCULATE OPERATIONAL RISK SCORE
--
-- Score balances:
-- 25% order-volume exposure
-- 25% revenue exposure
-- 25% late-delivery risk
-- 25% negative-review risk
-- ---------------------------------------------------------

risk_scored AS (

    SELECT
        *,

        ROUND(
            100.0
            *
            (
                0.25 * order_volume_percentile
                +
                0.25 * revenue_percentile
                +
                0.25 * late_delivery_percentile
                +
                0.25 * negative_review_percentile
            ),
            2
        ) AS operational_risk_score

    FROM risk_percentiles
),


-- ---------------------------------------------------------
-- 13. ASSIGN MANAGEMENT PRIORITY
--
-- High Priority:
-- - Above overall late-delivery benchmark
-- - Above overall negative-review benchmark
-- - Top 25% of entity type by revenue
--
-- Watch:
-- - At least one performance metric is worse than benchmark
-- - At least top 50% by revenue
-- ---------------------------------------------------------

prioritized AS (

    SELECT
        *,

        CASE
            WHEN
                late_delivery_rate_pct
                    > overall_late_delivery_rate_pct

                AND negative_review_rate_pct
                    > overall_negative_review_rate_pct

                AND revenue_percentile >= 0.75

            THEN 'High Priority'

            WHEN
                (
                    late_delivery_rate_pct
                        > overall_late_delivery_rate_pct

                    OR negative_review_rate_pct
                        > overall_negative_review_rate_pct
                )

                AND revenue_percentile >= 0.50

            THEN 'Watch'

            ELSE 'Monitor'

        END AS management_priority

    FROM risk_scored
)


-- ---------------------------------------------------------
-- 14. FINAL MANAGEMENT ACTION LIST
-- ---------------------------------------------------------

SELECT
    entity_type,

    entity_name,

    management_priority,

    operational_risk_score,

    orders,

    delivered_orders,

    reviewed_orders,

    merchandise_value,

    average_delivery_time_days,

    late_delivery_rate_pct,

    overall_late_delivery_rate_pct,

    late_delivery_gap_pp,

    average_review_score,

    overall_average_review_score,

    review_score_gap,

    negative_review_rate_pct,

    overall_negative_review_rate_pct,

    negative_review_gap_pp,

    ROUND(
        revenue_percentile * 100,
        2
    ) AS revenue_percentile_pct,

    ROUND(
        order_volume_percentile * 100,
        2
    ) AS order_volume_percentile_pct

FROM prioritized

ORDER BY
    CASE management_priority
        WHEN 'High Priority' THEN 1
        WHEN 'Watch' THEN 2
        ELSE 3
    END,

    operational_risk_score DESC;
   