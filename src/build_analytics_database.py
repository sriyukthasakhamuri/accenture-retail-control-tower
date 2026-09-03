from pathlib import Path

import duckdb


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROCESSED_DATA_PATH = Path("data/processed")
ANALYTICS_DATA_PATH = Path("data/analytics")

DATABASE_FILE = (
    ANALYTICS_DATA_PATH
    / "retail_analytics.duckdb"
)


# ---------------------------------------------------------
# TABLE CONFIGURATION
# ---------------------------------------------------------

TABLES = {
    "dim_customer": (
        PROCESSED_DATA_PATH
        / "dim_customer.csv"
    ),
    "dim_product": (
        PROCESSED_DATA_PATH
        / "dim_product.csv"
    ),
    "dim_seller": (
        PROCESSED_DATA_PATH
        / "dim_seller.csv"
    ),
    "dim_date": (
        PROCESSED_DATA_PATH
        / "dim_date.csv"
    ),
    "dim_geography": (
        PROCESSED_DATA_PATH
        / "dim_geography.csv"
    ),
    "fact_orders": (
        PROCESSED_DATA_PATH
        / "fact_orders.csv"
    ),
    "fact_order_items": (
        PROCESSED_DATA_PATH
        / "fact_order_items.csv"
    ),
    "fact_payments": (
        PROCESSED_DATA_PATH
        / "fact_payments.csv"
    ),
    "fact_reviews": (
        PROCESSED_DATA_PATH
        / "fact_reviews.csv"
    ),
}


# ---------------------------------------------------------
# BUILD ANALYTICS DATABASE
# ---------------------------------------------------------

def build_analytics_database():
    """
    Create a DuckDB analytical database from the
    processed dimensional model.
    """

    print("=" * 80)
    print("BUILDING ANALYTICS SQL DATABASE")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. CREATE DATABASE DIRECTORY
    # -----------------------------------------------------

    ANALYTICS_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # 2. CONNECT TO DUCKDB
    # -----------------------------------------------------

    connection = duckdb.connect(
        str(DATABASE_FILE)
    )

    print(
        "\nDatabase:"
    )

    print(
        DATABASE_FILE
    )

    # -----------------------------------------------------
    # 3. LOAD ANALYTICAL TABLES
    # -----------------------------------------------------

    for table_name, csv_file in TABLES.items():

        print(
            "\n" + "-" * 80
        )

        print(
            f"Loading {table_name}"
        )

        print(
            "-" * 80
        )

        if not csv_file.exists():
            raise FileNotFoundError(
                f"Missing processed file: "
                f"{csv_file}"
            )

        connection.execute(
            f"""
            CREATE OR REPLACE TABLE
            {table_name}
            AS
            SELECT *
            FROM read_csv_auto(
                '{csv_file}',
                header = true
            )
            """
        )

        row_count = (
            connection.execute(
                f"""
                SELECT COUNT(*)
                FROM {table_name}
                """
            )
            .fetchone()[0]
        )

        print(
            f"Rows loaded: "
            f"{row_count:,}"
        )

    # -----------------------------------------------------
    # 4. DISPLAY DATABASE TABLES
    # -----------------------------------------------------

    print(
        "\n" + "=" * 80
    )

    print(
        "DATABASE TABLES"
    )

    print(
        "=" * 80
    )

    tables = (
        connection.execute(
            """
            SHOW TABLES
            """
        )
        .fetchall()
    )

    for table in tables:
        print(
            table[0]
        )

    # -----------------------------------------------------
    # 5. VALIDATE TABLE COUNTS
    # -----------------------------------------------------

    print(
        "\n" + "=" * 80
    )

    print(
        "SQL TABLE ROW COUNTS"
    )

    print(
        "=" * 80
    )

    for table_name in TABLES:

        row_count = (
            connection.execute(
                f"""
                SELECT COUNT(*)
                FROM {table_name}
                """
            )
            .fetchone()[0]
        )

        print(
            f"{table_name:<25}"
            f"{row_count:>12,}"
        )

    # -----------------------------------------------------
    # 6. BASIC REFERENTIAL VALIDATION
    # -----------------------------------------------------

    print(
        "\n" + "=" * 80
    )

    print(
        "SQL RELATIONSHIP VALIDATION"
    )

    print(
        "=" * 80
    )

    missing_customer_orders = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM fact_orders AS o
            LEFT JOIN dim_customer AS c
                ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
            """
        )
        .fetchone()[0]
    )

    print(
        "\nOrders without customers:"
    )

    print(
        missing_customer_orders
    )

    missing_products = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM fact_order_items AS oi
            LEFT JOIN dim_product AS p
                ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL
            """
        )
        .fetchone()[0]
    )

    print(
        "\nOrder items without products:"
    )

    print(
        missing_products
    )

    missing_sellers = (
        connection.execute(
            """
            SELECT COUNT(*)
            FROM fact_order_items AS oi
            LEFT JOIN dim_seller AS s
                ON oi.seller_id = s.seller_id
            WHERE s.seller_id IS NULL
            """
        )
        .fetchone()[0]
    )

    print(
        "\nOrder items without sellers:"
    )

    print(
        missing_sellers
    )

    # -----------------------------------------------------
    # 7. CLOSE CONNECTION
    # -----------------------------------------------------

    connection.close()

    print(
        "\n" + "=" * 80
    )

    print(
        "ANALYTICS DATABASE BUILD COMPLETE"
    )

    print(
        "=" * 80
    )

    print(
        "\nCreated:"
    )

    print(
        DATABASE_FILE
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_analytics_database()