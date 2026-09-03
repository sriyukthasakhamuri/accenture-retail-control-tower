-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- PRODUCT & CATEGORY PERFORMANCE
--
-- Reporting grain:
-- One row = one product category
-- =========================================================


-- ---------------------------------------------------------
-- 1. AGGREGATE REVIEWS TO ORDER GRAIN
-- ---------------------------------------------------------

WITH review_by_order AS (

    SELECT
        order_id,

        AVG(review_score)
            AS average_review_score

    FROM fact_reviews

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 2. CREATE ORDER + CATEGORY GRAIN
--
-- One row = one order/category combination
--
-- This prevents orders containing multiple items in the
-- same category from being counted multiple times.
-- ---------------------------------------------------------

order_category AS (

    SELECT
        oi.order_id,

        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS product_category,

        COUNT(*)
            AS item_count,

        COUNT(
            DISTINCT oi.product_id
        ) AS unique_products,

        COUNT(
            DISTINCT oi.seller_id
        ) AS sellers_in_order_category,

        SUM(
            oi.price
        ) AS merchandise_value,

        SUM(
            oi.freight_value
        ) AS freight_value,

        SUM(
            oi.item_total_value
        ) AS item_value_including_freight

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
-- 3. ADD ORDER + REVIEW INFORMATION
-- ---------------------------------------------------------

category_analysis AS (

    SELECT
        oc.order_id,

        oc.product_category,

        oc.item_count,

        oc.unique_products,

        oc.sellers_in_order_category,

        oc.merchandise_value,

        oc.freight_value,

        oc.item_value_including_freight,

        o.is_delivered,

        o.is_late_delivery,

        o.delivery_time_days,

        o.delivery_delay_days,

        r.average_review_score

    FROM order_category AS oc

    INNER JOIN fact_orders AS o
        ON oc.order_id = o.order_id

    LEFT JOIN review_by_order AS r
        ON oc.order_id = r.order_id
),


-- ---------------------------------------------------------
-- 4. CATEGORY KPI SUMMARY
-- ---------------------------------------------------------

category_metrics AS (

    SELECT
        product_category,

        COUNT(
            DISTINCT order_id
        ) AS orders,

        SUM(
            item_count
        ) AS items_sold,

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
            SUM(merchandise_value)
            /
            NULLIF(
                SUM(item_count),
                0
            ),
            2
        ) AS average_item_price,

        ROUND(
            100.0
            *
            SUM(freight_value)
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
        ) AS negative_review_rate_pct

    FROM category_analysis

    GROUP BY
        product_category
)


-- ---------------------------------------------------------
-- 5. FINAL PRODUCT CATEGORY REPORT
-- ---------------------------------------------------------

SELECT
    product_category,

    orders,

    items_sold,

    merchandise_value,

    freight_value,

    item_value_including_freight,

    average_item_price,

    freight_share_pct,

    average_delivery_time_days,

    late_delivery_rate_pct,

    average_review_score,

    positive_review_rate_pct,

    negative_review_rate_pct

FROM category_metrics

ORDER BY
    merchandise_value DESC;