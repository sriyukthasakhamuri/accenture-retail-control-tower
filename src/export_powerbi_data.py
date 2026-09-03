from pathlib import Path

import duckdb


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "analytics"
    / "retail_analytics.duckdb"
)

SQL_DIR = PROJECT_ROOT / "sql"

OUTPUT_DIR = PROJECT_ROOT / "data" / "powerbi"


# =========================================================
# SQL REPORTS TO EXPORT
# =========================================================

SQL_EXPORTS = {
    "executive_kpis.csv": "01_executive_kpis.sql",
    "monthly_performance.csv": "02_monthly_performance.sql",
    "product_performance.csv": "03_product_performance.sql",
    "seller_performance.csv": "04_seller_performance.sql",
    "geographic_performance.csv": "05_geographic_performance.sql",
    "customer_behavior.csv": "06_customer_behavior.sql",
    "payment_behavior.csv": "07_payment_behavior.sql",
    "delivery_operations.csv": "08_delivery_operations.sql",
    "operational_risk.csv": "09_operational_risk.sql",
}


# =========================================================
# HELPER FUNCTION
# =========================================================

def read_sql(file_name):
    sql_path = SQL_DIR / file_name

    return (
        sql_path
        .read_text()
        .strip()
        .rstrip(";")
    )


# =========================================================
# EXPORT VALIDATED SQL REPORTS
# =========================================================

def export_sql_reports(connection):

    print("=" * 80)
    print("POWER BI DATA EXPORT")
    print("=" * 80)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for output_file, sql_file in SQL_EXPORTS.items():

        print()
        print(f"Running: {sql_file}")

        sql = read_sql(sql_file)

        df = connection.execute(
            sql
        ).df()

        output_path = OUTPUT_DIR / output_file

        df.to_csv(
            output_path,
            index=False
        )

        print(
            f"Saved: {output_file}"
        )

        print(
            f"Rows: {len(df):,}"
        )


# =========================================================
# CREATE CUSTOMER SEGMENT SUMMARY
# =========================================================

def export_customer_segment_summary(connection):

    print()
    print("=" * 80)
    print("CUSTOMER SEGMENT SUMMARY")
    print("=" * 80)

    customer_sql = read_sql(
        "06_customer_behavior.sql"
    )

    connection.execute(
        """
        CREATE OR REPLACE TEMP VIEW
        customer_behavior_export AS
        """
        + customer_sql
    )

    summary = connection.execute(
        """
        SELECT
            customer_type,

            order_frequency_segment,

            COUNT(*) AS customers,

            SUM(
                lifetime_orders
            ) AS total_orders,

            ROUND(
                SUM(
                    lifetime_payment_value
                ),
                2
            ) AS total_payment_value,

            ROUND(
                AVG(
                    lifetime_payment_value
                ),
                2
            ) AS average_customer_value,

            ROUND(
                AVG(
                    average_order_value
                ),
                2
            ) AS average_order_value,

            ROUND(
                AVG(
                    average_review_score
                ),
                2
            ) AS average_review_score,

            ROUND(
                AVG(
                    average_delivery_time_days
                ),
                2
            ) AS average_delivery_time_days

        FROM customer_behavior_export

        GROUP BY
            customer_type,
            order_frequency_segment

        ORDER BY
            customer_type,
            order_frequency_segment
        """
    ).df()

    output_path = (
        OUTPUT_DIR
        / "customer_segment_summary.csv"
    )

    summary.to_csv(
        output_path,
        index=False
    )

    print(
        "Saved: customer_segment_summary.csv"
    )

    print(
        f"Rows: {len(summary):,}"
    )


# =========================================================
# VALIDATE EXPORTED FILES
# =========================================================

def validate_exports():

    print()
    print("=" * 80)
    print("EXPORT VALIDATION")
    print("=" * 80)

    expected_files = (
        list(SQL_EXPORTS.keys())
        + ["customer_segment_summary.csv"]
    )

    for file_name in expected_files:

        file_path = OUTPUT_DIR / file_name

        if not file_path.exists():

            raise FileNotFoundError(
                f"Missing Power BI export: {file_name}"
            )

        file_size = file_path.stat().st_size

        print(
            f"{file_name:<35}"
            f"{file_size / 1024:>10.2f} KB"
        )

    print()
    print("All Power BI exports created successfully.")


# =========================================================
# RUN PROGRAM
# =========================================================

def main():

    if not DATABASE_FILE.exists():

        raise FileNotFoundError(
            f"Analytics database not found: "
            f"{DATABASE_FILE}"
        )

    connection = duckdb.connect(
        str(DATABASE_FILE)
    )

    try:

        export_sql_reports(
            connection
        )

        export_customer_segment_summary(
            connection
        )

    finally:

        connection.close()

    validate_exports()

    print()
    print("=" * 80)
    print("POWER BI EXPORT COMPLETE")
    print("=" * 80)

    print()
    print(
        f"Dashboard-ready files saved to:"
    )

    print(
        OUTPUT_DIR
    )


if __name__ == "__main__":
    main()