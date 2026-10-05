from pathlib import Path

import duckdb
import pytest


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

DATABASE_FILE = Path(
    "data/analytics/retail_analytics.duckdb"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

@pytest.fixture(scope="module")
def connection():
    """
    Open the analytical DuckDB database once for this
    test module and close it after all tests complete.
    """

    if not DATABASE_FILE.exists():
        pytest.fail(
            f"Analytics database does not exist: "
            f"{DATABASE_FILE}"
        )

    con = duckdb.connect(
        str(DATABASE_FILE),
        read_only=True,
    )

    yield con

    con.close()


# =========================================================
# 1. REQUIRED TABLES
# =========================================================

def test_required_tables_exist(connection):
    """
    Verify that all required fact and dimension tables
    exist in the analytical database.
    """

    required_tables = {
        "dim_customer",
        "dim_product",
        "dim_seller",
        "dim_date",
        "dim_geography",
        "fact_orders",
        "fact_order_items",
        "fact_payments",
        "fact_reviews",
    }

    existing_tables = {
        row[0]
        for row in connection.execute(
            "SHOW TABLES"
        ).fetchall()
    }

    missing_tables = (
        required_tables - existing_tables
    )

    assert not missing_tables, (
        "Missing required tables: "
        f"{sorted(missing_tables)}"
    )


# =========================================================
# 2. PRIMARY / BUSINESS KEY UNIQUENESS
# =========================================================

@pytest.mark.parametrize(
    "table_name,key_column",
    [
        ("dim_customer", "customer_id"),
        ("dim_product", "product_id"),
        ("dim_seller", "seller_id"),
        ("dim_date", "date_key"),
        ("fact_orders", "order_id"),
    ],
)
def test_unique_keys(
    connection,
    table_name,
    key_column,
):
    """
    Verify that key columns expected to be unique
    contain no duplicate values.
    """

    duplicate_count = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT
                {key_column}
            FROM {table_name}
            GROUP BY {key_column}
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    assert duplicate_count == 0, (
        f"{table_name}.{key_column} "
        f"contains {duplicate_count} duplicate keys."
    )


# =========================================================
# 3. REQUIRED KEY NULL CHECKS
# =========================================================

@pytest.mark.parametrize(
    "table_name,key_column",
    [
        ("dim_customer", "customer_id"),
        ("dim_product", "product_id"),
        ("dim_seller", "seller_id"),
        ("dim_date", "date_key"),
        ("fact_orders", "order_id"),
        ("fact_order_items", "order_id"),
        ("fact_order_items", "product_id"),
        ("fact_order_items", "seller_id"),
        ("fact_payments", "order_id"),
        ("fact_reviews", "order_id"),
    ],
)
def test_required_keys_not_null(
    connection,
    table_name,
    key_column,
):
    """
    Verify that required analytical keys are populated.
    """

    null_count = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {table_name}
        WHERE {key_column} IS NULL
        """
    ).fetchone()[0]

    assert null_count == 0, (
        f"{table_name}.{key_column} "
        f"contains {null_count} NULL values."
    )


# =========================================================
# 4. CUSTOMER REFERENTIAL INTEGRITY
# =========================================================

def test_orders_have_valid_customers(connection):
    """
    Every order customer_id must resolve to dim_customer.
    """

    missing_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_orders AS o

        LEFT JOIN dim_customer AS c
            ON o.customer_id = c.customer_id

        WHERE c.customer_id IS NULL
        """
    ).fetchone()[0]

    assert missing_count == 0, (
        f"{missing_count} orders do not have "
        "a matching customer dimension record."
    )


# =========================================================
# 5. PRODUCT REFERENTIAL INTEGRITY
# =========================================================

def test_order_items_have_valid_products(connection):
    """
    Every order-item product_id must resolve to dim_product.
    """

    missing_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_order_items AS oi

        LEFT JOIN dim_product AS p
            ON oi.product_id = p.product_id

        WHERE p.product_id IS NULL
        """
    ).fetchone()[0]

    assert missing_count == 0, (
        f"{missing_count} order items do not have "
        "a matching product dimension record."
    )


# =========================================================
# 6. SELLER REFERENTIAL INTEGRITY
# =========================================================

def test_order_items_have_valid_sellers(connection):
    """
    Every order-item seller_id must resolve to dim_seller.
    """

    missing_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_order_items AS oi

        LEFT JOIN dim_seller AS s
            ON oi.seller_id = s.seller_id

        WHERE s.seller_id IS NULL
        """
    ).fetchone()[0]

    assert missing_count == 0, (
        f"{missing_count} order items do not have "
        "a matching seller dimension record."
    )


# =========================================================
# 7. ORDER REFERENTIAL INTEGRITY
# =========================================================

@pytest.mark.parametrize(
    "table_name",
    [
        "fact_order_items",
        "fact_payments",
        "fact_reviews",
    ],
)
def test_fact_records_have_valid_orders(
    connection,
    table_name,
):
    """
    Child fact records must resolve to fact_orders.
    """

    missing_count = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {table_name} AS child

        LEFT JOIN fact_orders AS o
            ON child.order_id = o.order_id

        WHERE o.order_id IS NULL
        """
    ).fetchone()[0]

    assert missing_count == 0, (
        f"{missing_count} records in {table_name} "
        "do not have a matching order."
    )


# =========================================================
# 8. FINANCIAL VALUE VALIDATION
# =========================================================

def test_order_item_prices_are_non_negative(connection):
    """
    Merchandise and freight values should not be negative.
    """

    invalid_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_order_items
        WHERE
            price < 0
            OR freight_value < 0
            OR item_total_value < 0
        """
    ).fetchone()[0]

    assert invalid_count == 0, (
        f"{invalid_count} order-item records contain "
        "negative financial values."
    )


def test_payment_values_are_non_negative(connection):
    """
    Payment values should not be negative.
    """

    invalid_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_payments
        WHERE payment_value < 0
        """
    ).fetchone()[0]

    assert invalid_count == 0, (
        f"{invalid_count} payment records contain "
        "negative payment values."
    )


# =========================================================
# 9. REVIEW SCORE BUSINESS RULE
# =========================================================

def test_review_scores_are_valid(connection):
    """
    Review scores must remain within the expected
    one-to-five rating scale.
    """

    invalid_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_reviews
        WHERE
            review_score IS NOT NULL
            AND (
                review_score < 1
                OR review_score > 5
            )
        """
    ).fetchone()[0]

    assert invalid_count == 0, (
        f"{invalid_count} review records contain "
        "scores outside the 1-5 range."
    )


# =========================================================
# 10. DELIVERY BUSINESS RULES
# =========================================================

def test_delivery_time_is_non_negative(connection):
    """
    Delivered orders should not have negative
    delivery durations.
    """

    invalid_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_orders
        WHERE
            is_delivered = 1
            AND delivery_time_days < 0
        """
    ).fetchone()[0]

    assert invalid_count == 0, (
        f"{invalid_count} delivered orders contain "
        "negative delivery durations."
    )


def test_binary_delivery_flags(connection):
    """
    Delivery flags should only contain 0, 1, or NULL.
    """

    invalid_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM fact_orders
        WHERE
            (
                is_delivered IS NOT NULL
                AND is_delivered NOT IN (0, 1)
            )
            OR
            (
                is_late_delivery IS NOT NULL
                AND is_late_delivery NOT IN (0, 1)
            )
        """
    ).fetchone()[0]

    assert invalid_count == 0, (
        f"{invalid_count} orders contain "
        "invalid delivery flag values."
    )


# =========================================================
# 11. DATE DIMENSION UNIQUENESS
# =========================================================

def test_date_dimension_has_unique_dates(connection):
    """
    dim_date should contain exactly one row per
    calendar date.
    """

    result = connection.execute(
        """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT date) AS unique_dates
        FROM dim_date
        """
    ).fetchone()

    total_rows = result[0]
    unique_dates = result[1]

    assert total_rows == unique_dates, (
        "dim_date contains duplicate calendar dates."
    )


# =========================================================
# 12. DATE DIMENSION CONTINUITY
# =========================================================

def test_date_dimension_is_continuous(connection):
    """
    Number of rows in dim_date must equal the number
    of calendar days between MIN(date) and MAX(date),
    inclusive.
    """

    result = connection.execute(
        """
        SELECT
            COUNT(*) AS actual_rows,

            DATE_DIFF(
                'day',
                MIN(date),
                MAX(date)
            ) + 1 AS expected_rows

        FROM dim_date
        """
    ).fetchone()

    actual_rows = result[0]
    expected_rows = result[1]

    assert actual_rows == expected_rows, (
        "dim_date is not a continuous calendar. "
        f"Expected {expected_rows} rows but "
        f"found {actual_rows}."
    )


# =========================================================
# 13. DATE ATTRIBUTE CONSISTENCY
# =========================================================

def test_date_attributes_match_calendar_date(connection):
    """
    Stored year/month attributes should agree with
    the underlying calendar date.
    """

    invalid_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM dim_date
        WHERE
            year != YEAR(date)
            OR month_number != MONTH(date)
            OR year_month_sort
                != (
                    YEAR(date) * 100
                    + MONTH(date)
                )
        """
    ).fetchone()[0]

    assert invalid_count == 0, (
        f"{invalid_count} dim_date records contain "
        "inconsistent calendar attributes."
    )