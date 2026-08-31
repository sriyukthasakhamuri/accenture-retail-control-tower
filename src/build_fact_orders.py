from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

ORDERS_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_orders_dataset.csv"
)

FACT_ORDERS_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "fact_orders.csv"
)


# ---------------------------------------------------------
# BUILD FACT ORDERS
# ---------------------------------------------------------

def build_fact_orders():
    """
    Build an analytics-ready order fact table
    from the raw Olist orders dataset.
    """

    print("=" * 80)
    print("BUILDING FACT_ORDERS")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW ORDERS
    # -----------------------------------------------------

    orders_df = pd.read_csv(
        ORDERS_SOURCE_FILE
    )

    print(
        f"\nRaw order rows: "
        f"{len(orders_df):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE SOURCE GRAIN
    # -----------------------------------------------------

    unique_orders = (
        orders_df["order_id"].nunique()
    )

    print(
        f"Unique order IDs: "
        f"{unique_orders:,}"
    )

    if len(orders_df) != unique_orders:
        raise ValueError(
            "Orders source is not "
            "one row per order."
        )

    # -----------------------------------------------------
    # 3. CONVERT TIMESTAMP COLUMNS
    # -----------------------------------------------------

    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in timestamp_columns:
        orders_df[column] = pd.to_datetime(
            orders_df[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # 4. CREATE PURCHASE DATE
    # -----------------------------------------------------

    orders_df["order_purchase_date"] = (
        orders_df[
            "order_purchase_timestamp"
        ].dt.date
    )

    # -----------------------------------------------------
    # 5. CREATE STATUS FLAGS
    # -----------------------------------------------------

    orders_df["is_delivered"] = (
        orders_df["order_status"]
        .eq("delivered")
        .astype(int)
    )

    orders_df["is_canceled"] = (
        orders_df["order_status"]
        .eq("canceled")
        .astype(int)
    )

    # -----------------------------------------------------
    # 6. CALCULATE APPROVAL TIME
    # -----------------------------------------------------

    orders_df["approval_time_hours"] = (
        (
            orders_df["order_approved_at"]
            - orders_df[
                "order_purchase_timestamp"
            ]
        )
        .dt.total_seconds()
        / 3600
    )

    # -----------------------------------------------------
    # 7. CALCULATE CARRIER HANDOFF TIME
    # -----------------------------------------------------

    orders_df[
        "carrier_handoff_time_hours"
    ] = (
        (
            orders_df[
                "order_delivered_carrier_date"
            ]
            - orders_df[
                "order_purchase_timestamp"
            ]
        )
        .dt.total_seconds()
        / 3600
    )

    # -----------------------------------------------------
    # 8. CALCULATE DELIVERY TIME
    # -----------------------------------------------------

    orders_df["delivery_time_days"] = (
        (
            orders_df[
                "order_delivered_customer_date"
            ]
            - orders_df[
                "order_purchase_timestamp"
            ]
        )
        .dt.total_seconds()
        / 86400
    )

    # -----------------------------------------------------
    # 9. CALCULATE DELIVERY DELAY
    # -----------------------------------------------------

    orders_df["delivery_delay_days"] = (
        (
            orders_df[
                "order_delivered_customer_date"
            ]
            - orders_df[
                "order_estimated_delivery_date"
            ]
        )
        .dt.total_seconds()
        / 86400
    )

    # -----------------------------------------------------
    # 10. CREATE LATE DELIVERY FLAG
    # -----------------------------------------------------

    orders_df["is_late_delivery"] = (
        (
            orders_df["is_delivered"] == 1
        )
        &
        (
            orders_df[
                "delivery_delay_days"
            ] > 0
        )
    ).astype(int)

    # -----------------------------------------------------
    # 11. SELECT FACT TABLE COLUMNS
    # -----------------------------------------------------

    fact_orders = orders_df[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_purchase_date",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "approval_time_hours",
            "carrier_handoff_time_hours",
            "delivery_time_days",
            "delivery_delay_days",
            "is_delivered",
            "is_canceled",
            "is_late_delivery",
        ]
    ].copy()

    # -----------------------------------------------------
    # 12. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(fact_orders)

    output_unique_orders = (
        fact_orders["order_id"].nunique()
    )

    print(
        f"\nProcessed rows: "
        f"{output_rows:,}"
    )

    print(
        f"Processed unique orders: "
        f"{output_unique_orders:,}"
    )

    if output_rows != len(orders_df):
        raise ValueError(
            "Row count changed during "
            "fact_orders transformation."
        )

    if output_rows != output_unique_orders:
        raise ValueError(
            "fact_orders grain validation failed."
        )

    # -----------------------------------------------------
    # 13. QUALITY / KPI SUMMARY
    # -----------------------------------------------------

    print(
        "\nDelivered orders: "
        f"{fact_orders['is_delivered'].sum():,}"
    )

    print(
        "Canceled orders: "
        f"{fact_orders['is_canceled'].sum():,}"
    )

    print(
        "Late delivered orders: "
        f"{fact_orders['is_late_delivery'].sum():,}"
    )

    print(
        "\nMissing delivery times: "
        f"{fact_orders['delivery_time_days'].isna().sum():,}"
    )

    # -----------------------------------------------------
    # 14. SAVE PROCESSED TABLE
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    fact_orders.to_csv(
        FACT_ORDERS_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved fact_orders to:"
    )

    print(
        FACT_ORDERS_OUTPUT_FILE
    )

    print(
        "\nFACT_ORDERS BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_fact_orders()