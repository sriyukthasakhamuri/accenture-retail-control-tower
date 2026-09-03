-- =========================================================
-- ENTERPRISE RETAIL ANALYTICS & OPERATIONS CONTROL TOWER
-- PAYMENT & INSTALLMENT BEHAVIOR
--
-- Reporting grain:
-- One row = one payment type
-- =========================================================


-- ---------------------------------------------------------
-- 1. NORMALIZE PAYMENT RECORDS
-- ---------------------------------------------------------

WITH payment_base AS (

    SELECT
        order_id,

        COALESCE(
            payment_type,
            'Unknown'
        ) AS payment_type,

        payment_sequential,

        payment_installments,

        payment_value

    FROM fact_payments
),


-- ---------------------------------------------------------
-- 2. COUNT PAYMENT METHODS USED PER ORDER
-- ---------------------------------------------------------

order_method_counts AS (

    SELECT
        order_id,

        COUNT(
            DISTINCT payment_type
        ) AS payment_methods_used,

        SUM(
            payment_value
        ) AS total_order_payment_value

    FROM payment_base

    GROUP BY
        order_id
),


-- ---------------------------------------------------------
-- 3. AGGREGATE TO ORDER + PAYMENT TYPE GRAIN
--
-- One order can contain multiple payment records.
-- We first combine records belonging to the same
-- payment method within the order.
-- ---------------------------------------------------------

payment_type_order AS (

    SELECT
        order_id,

        payment_type,

        COUNT(*)
            AS payment_records,

        SUM(
            payment_value
        ) AS payment_value,

        SUM(
            payment_installments
        ) AS installment_total,

        MAX(
            payment_installments
        ) AS max_installments,

        SUM(
            CASE
                WHEN payment_installments > 1
                THEN 1
                ELSE 0
            END
        ) AS multi_installment_records

    FROM payment_base

    GROUP BY
        order_id,
        payment_type
),


-- ---------------------------------------------------------
-- 4. ADD ORDER-LEVEL PAYMENT BEHAVIOR
-- ---------------------------------------------------------

payment_analysis AS (

    SELECT
        p.order_id,

        p.payment_type,

        p.payment_records,

        p.payment_value,

        p.installment_total,

        p.max_installments,

        p.multi_installment_records,

        o.payment_methods_used,

        o.total_order_payment_value

    FROM payment_type_order AS p

    INNER JOIN order_method_counts AS o
        ON p.order_id = o.order_id
),


-- ---------------------------------------------------------
-- 5. CALCULATE PAYMENT-TYPE KPIS
-- ---------------------------------------------------------

payment_type_metrics AS (

    SELECT
        payment_type,

        COUNT(
            DISTINCT order_id
        ) AS orders_using_payment_type,

        SUM(
            payment_records
        ) AS payment_records,

        ROUND(
            SUM(
                payment_value
            ),
            2
        ) AS total_payment_value,

        ROUND(
            AVG(
                payment_value
            ),
            2
        ) AS average_payment_value_per_order,

        ROUND(
            SUM(payment_value)
            /
            NULLIF(
                SUM(payment_records),
                0
            ),
            2
        ) AS average_payment_record_value,

        ROUND(
            SUM(installment_total)
            /
            NULLIF(
                SUM(payment_records),
                0
            ),
            2
        ) AS average_installments,

        MAX(
            max_installments
        ) AS maximum_installments,

        SUM(
            multi_installment_records
        ) AS multi_installment_records,

        ROUND(
            100.0
            *
            SUM(
                multi_installment_records
            )
            /
            NULLIF(
                SUM(payment_records),
                0
            ),
            2
        ) AS multi_installment_record_rate_pct,

        SUM(
            CASE
                WHEN payment_methods_used > 1
                THEN 1
                ELSE 0
            END
        ) AS multi_method_orders,

        ROUND(
            100.0
            *
            SUM(
                CASE
                    WHEN payment_methods_used > 1
                    THEN 1
                    ELSE 0
                END
            )
            /
            NULLIF(
                COUNT(
                    DISTINCT order_id
                ),
                0
            ),
            2
        ) AS multi_method_order_rate_pct

    FROM payment_analysis

    GROUP BY
        payment_type
),


-- ---------------------------------------------------------
-- 6. OVERALL PAYMENT TOTALS
-- ---------------------------------------------------------

payment_totals AS (

    SELECT
        SUM(
            payment_records
        ) AS all_payment_records,

        SUM(
            total_payment_value
        ) AS all_payment_value

    FROM payment_type_metrics
),


-- ---------------------------------------------------------
-- 7. ADD PAYMENT SHARES
-- ---------------------------------------------------------

payment_enriched AS (

    SELECT
        p.payment_type,

        p.orders_using_payment_type,

        p.payment_records,

        p.total_payment_value,

        ROUND(
            100.0
            *
            p.payment_records
            /
            NULLIF(
                t.all_payment_records,
                0
            ),
            2
        ) AS payment_record_share_pct,

        ROUND(
            100.0
            *
            p.total_payment_value
            /
            NULLIF(
                t.all_payment_value,
                0
            ),
            2
        ) AS payment_value_share_pct,

        p.average_payment_value_per_order,

        p.average_payment_record_value,

        p.average_installments,

        p.maximum_installments,

        p.multi_installment_records,

        p.multi_installment_record_rate_pct,

        p.multi_method_orders,

        p.multi_method_order_rate_pct

    FROM payment_type_metrics AS p

    CROSS JOIN payment_totals AS t
)


-- ---------------------------------------------------------
-- 8. FINAL PAYMENT REPORT
-- ---------------------------------------------------------

SELECT
    payment_type,

    orders_using_payment_type,

    payment_records,

    total_payment_value,

    payment_record_share_pct,

    payment_value_share_pct,

    average_payment_value_per_order,

    average_payment_record_value,

    average_installments,

    maximum_installments,

    multi_installment_records,

    multi_installment_record_rate_pct,

    multi_method_orders,

    multi_method_order_rate_pct

FROM payment_enriched

ORDER BY
    total_payment_value DESC;