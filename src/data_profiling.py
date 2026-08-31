from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROFILE_OUTPUT_PATH = Path("docs/source_data_profile.csv")


# ---------------------------------------------------------
# GENERIC DATA PROFILING FUNCTION
# ---------------------------------------------------------

def profile_csv(file_path):
    """
    Profile one CSV file and return summary statistics.
    """

    df = pd.read_csv(file_path)

    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum())

    missing_percent = (df.isna().sum() / len(df)) * 100

    print("\nMissing value percentage:")
    print(missing_percent.round(2))

    duplicate_rows = df.duplicated().sum()

    print("\nDuplicate rows:")
    print(duplicate_rows)

    print("\nSample rows:")
    print(df.head(3))

    # Count columns that contain at least one missing value
    columns_with_missing = (df.isna().sum() > 0).sum()

    # Count all missing cells in the dataset
    total_missing_values = df.isna().sum().sum()

    # Return summary information
    return {
        "dataset": file_path.name,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "duplicate_rows": duplicate_rows,
        "columns_with_missing_values": columns_with_missing,
        "total_missing_values": total_missing_values,
    }


# ---------------------------------------------------------
# PROFILE ALL RAW DATASETS
# ---------------------------------------------------------

def profile_all_datasets():
    """
    Profile every CSV in data/raw and create
    a consolidated source-data profiling report.
    """

    csv_files = sorted(RAW_DATA_PATH.glob("*.csv"))

    print(f"\nFound {len(csv_files)} CSV files.")

    profile_results = []

    for file_path in csv_files:

        result = profile_csv(file_path)

        profile_results.append(result)

    profile_summary = pd.DataFrame(profile_results)

    profile_summary.to_csv(
        PROFILE_OUTPUT_PATH,
        index=False
    )

    print("\n" + "=" * 80)
    print("SOURCE DATA PROFILING SUMMARY")
    print("=" * 80)

    print(profile_summary.to_string(index=False))

    print(
        f"\nProfiling report saved to: "
        f"{PROFILE_OUTPUT_PATH}"
    )


# ---------------------------------------------------------
# ORDERS-SPECIFIC DATA QUALITY INVESTIGATION
# ---------------------------------------------------------

def investigate_orders():
    """
    Perform additional business-specific data-quality
    checks on the orders dataset.
    """

    orders_file = (
        RAW_DATA_PATH /
        "olist_orders_dataset.csv"
    )

    orders_df = pd.read_csv(orders_file)

    print("\n" + "=" * 80)
    print(
        "ORDERS DATASET — "
        "ADDITIONAL DATA QUALITY INVESTIGATION"
    )
    print("=" * 80)

    # -----------------------------------------------------
    # Verify order grain / candidate primary key
    # -----------------------------------------------------

    print("\nTotal order rows:")
    print(len(orders_df))

    print("\nUnique order IDs:")
    print(
        orders_df["order_id"].nunique()
    )

    # -----------------------------------------------------
    # Order lifecycle statuses
    # -----------------------------------------------------

    print("\nOrder status distribution:")

    print(
        orders_df[
            "order_status"
        ].value_counts()
    )

    # -----------------------------------------------------
    # Missing customer delivery timestamps
    # -----------------------------------------------------

    print(
        "\nMissing delivery dates "
        "by order status:"
    )

    missing_delivery_by_status = (
        orders_df[
            orders_df[
                "order_delivered_customer_date"
            ].isna()
        ]["order_status"]
        .value_counts()
    )

    print(missing_delivery_by_status)

    # -----------------------------------------------------
    # Missing approval timestamps
    # -----------------------------------------------------

    print(
        "\nMissing approval dates "
        "by order status:"
    )

    missing_approval_by_status = (
        orders_df[
            orders_df[
                "order_approved_at"
            ].isna()
        ]["order_status"]
        .value_counts()
    )

    print(missing_approval_by_status)

    # -----------------------------------------------------
    # Missing carrier timestamps
    # -----------------------------------------------------

    print(
        "\nMissing carrier dates "
        "by order status:"
    )

    missing_carrier_by_status = (
        orders_df[
            orders_df[
                "order_delivered_carrier_date"
            ].isna()
        ]["order_status"]
        .value_counts()
    )

    print(missing_carrier_by_status)

    # -----------------------------------------------------
    # Delivered orders missing carrier timestamp
    # -----------------------------------------------------

    print(
        "\nDelivered orders "
        "missing carrier date:"
    )

    delivered_missing_carrier = orders_df[
        (
            orders_df["order_status"]
            == "delivered"
        )
        &
        (
            orders_df[
                "order_delivered_carrier_date"
            ].isna()
        )
    ]

    print(delivered_missing_carrier)

    # -----------------------------------------------------
    # Delivered orders missing customer delivery timestamp
    # -----------------------------------------------------

    print(
        "\nDelivered orders missing "
        "customer delivery date:"
    )

    delivered_missing_customer_date = (
        orders_df[
            (
                orders_df["order_status"]
                == "delivered"
            )
            &
            (
                orders_df[
                    "order_delivered_customer_date"
                ].isna()
            )
        ]
    )

    print(
        delivered_missing_customer_date
    )

    # -----------------------------------------------------
    # Delivered orders missing approval timestamp
    # -----------------------------------------------------

    print(
        "\nDelivered orders "
        "missing approval date:"
    )

    delivered_missing_approval = (
        orders_df[
            (
                orders_df["order_status"]
                == "delivered"
            )
            &
            (
                orders_df[
                    "order_approved_at"
                ].isna()
            )
        ]
    )

    print(delivered_missing_approval)


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":

    profile_all_datasets()

    investigate_orders()