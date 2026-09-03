-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- SELLER PERFORMANCE ANALYSIS
--
-- Reporting grain:
-- One row = one seller
-- =========================================================


-- ---------------------------------------------------------
-- 1. AGGREGATE ITEMS TO SELLER + ORDER GRAIN
--
-- One row = one seller participating in one order
-- ---------------------------------------------------------

WITH seller_order AS (

    SELECT
        seller_id,

        order_id,

        COUNT(*)
            AS items_sold,

        COUNT(
            DISTINCT product_id
        ) AS products_in_order,

        SUM(
            price
        ) AS merchandise_value,

        SUM(
            freight_value
        ) AS freight_value,

        SUM(
            item_total_value
        ) AS item_value_including_freight

    FROM fact_order_items

    GROUP BY
        seller_id,
        order_id
),


-- ---------------------------------------------------------
-- 2. COUNT UNIQUE PRODUCTS SOLD BY EACH SELLER
-- ---------------------------------------------------------

seller_products AS (

    SELECT
        seller_id,

        COUNT(
            DISTINCT product_id
        ) AS unique_products_sold

    FROM fact_order_items

    GROUP BY
        seller_id
),


-- ---------------------------------------------------------
-- 3. AGGREGATE REVIEWS TO ORDER GRAIN
-- ---------------------------------------------------------

review_by_order AS (

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
-- 4. CREATE SELLER + ORDER ANALYTICAL DATASET
-- ---------------------------------------------------------

seller_order_analysis AS (

    SELECT
        so.seller_id,

        so.order_id,

        so.items_sold,

        so.merchandise_value,

        so.freight_value,

        so.item_value_including_freight,

        o.customer_id,

        c.customer_unique_id,

        o.is_delivered,

        o.is_late_delivery,

        o.delivery_time_days,

        o.delivery_delay_days,

        r.average_review_score

    FROM seller_order AS so

    INNER JOIN fact_orders AS o
        ON so.order_id = o.order_id

    LEFT JOIN dim_customer AS c
        ON o.customer_id = c.customer_id

    LEFT JOIN review_by_order AS r
        ON so.order_id = r.order_id
),


-- ---------------------------------------------------------
-- 5. CALCULATE SELLER KPIS
-- ---------------------------------------------------------

seller_metrics AS (

    SELECT
        soa.seller_id,

        COUNT(
            DISTINCT soa.order_id
        ) AS orders,

        COUNT(
            DISTINCT soa.customer_unique_id
        ) AS unique_customers,

        SUM(
            soa.items_sold
        ) AS items_sold,

        ROUND(
            SUM(
                soa.merchandise_value
            ),
            2
        ) AS merchandise_value,

        ROUND(
            SUM(
                soa.freight_value
            ),
            2
        ) AS freight_value,

        ROUND(
            SUM(
                soa.item_value_including_freight
            ),
            2
        ) AS item_value_including_freight,

        ROUND(
            AVG(
                soa.merchandise_value
            ),
            2
        ) AS average_seller_order_value,

        ROUND(
            SUM(soa.merchandise_value)
            /
            NULLIF(
                SUM(soa.items_sold),
                0
            ),
            2
        ) AS average_item_price,

        ROUND(
            100.0
            *
            SUM(soa.freight_value)
            /
            NULLIF(
                SUM(
                    soa.item_value_including_freight
                ),
                0
            ),
            2
        ) AS freight_share_pct,

        SUM(
            CASE
                WHEN soa.is_delivered = 1
                THEN 1
                ELSE 0
            END
        ) AS delivered_orders,

        ROUND(
            AVG(
                CASE
                    WHEN soa.is_delivered = 1
                    THEN soa.delivery_time_days
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
                        soa.is_delivered = 1
                        AND soa.delivery_delay_days IS NOT NULL
                    THEN soa.is_late_delivery
                END
            ),
            2
        ) AS late_delivery_rate_pct,

        ROUND(
            AVG(
                soa.average_review_score
            ),
            2
        ) AS average_review_score,

        ROUND(
            100.0
            *
            AVG(
                CASE
                    WHEN soa.average_review_score >= 4
                    THEN 1.0

                    WHEN soa.average_review_score IS NOT NULL
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
                    WHEN soa.average_review_score <= 2
                    THEN 1.0

                    WHEN soa.average_review_score IS NOT NULL
                    THEN 0.0
                END
            ),
            2
        ) AS negative_review_rate_pct

    FROM seller_order_analysis AS soa

    GROUP BY
        soa.seller_id
),


-- ---------------------------------------------------------
-- 6. ADD SELLER DIMENSION INFORMATION
-- ---------------------------------------------------------

seller_enriched AS (

    SELECT
        sm.seller_id,

        s.seller_city,

        s.seller_state,

        sp.unique_products_sold,

        sm.orders,

        sm.unique_customers,

        sm.items_sold,

        sm.merchandise_value,

        sm.freight_value,

        sm.item_value_including_freight,

        sm.average_seller_order_value,

        sm.average_item_price,

        sm.freight_share_pct,

        sm.delivered_orders,

        sm.average_delivery_time_days,

        sm.late_delivery_rate_pct,

        sm.average_review_score,

        sm.positive_review_rate_pct,

        sm.negative_review_rate_pct

    FROM seller_metrics AS sm

    LEFT JOIN dim_seller AS s
        ON sm.seller_id = s.seller_id

    LEFT JOIN seller_products AS sp
        ON sm.seller_id = sp.seller_id
),


-- ---------------------------------------------------------
-- 7. ADD PERFORMANCE RANKINGS
-- ---------------------------------------------------------

seller_ranked AS (

    SELECT
        *,

        DENSE_RANK() OVER (
            ORDER BY
                merchandise_value DESC
        ) AS revenue_rank,

        DENSE_RANK() OVER (
            ORDER BY
                orders DESC
        ) AS order_volume_rank

    FROM seller_enriched
)


-- ---------------------------------------------------------
-- 8. FINAL SELLER REPORT
-- ---------------------------------------------------------

SELECT
    seller_id,

    seller_city,

    seller_state,

    revenue_rank,

    order_volume_rank,

    unique_products_sold,

    orders,

    unique_customers,

    items_sold,

    merchandise_value,

    freight_value,

    item_value_including_freight,

    average_seller_order_value,

    average_item_price,

    freight_share_pct,

    delivered_orders,

    average_delivery_time_days,

    late_delivery_rate_pct,

    average_review_score,

    positive_review_rate_pct,

    negative_review_rate_pct

FROM seller_ranked

ORDER BY
    merchandise_value DESC;