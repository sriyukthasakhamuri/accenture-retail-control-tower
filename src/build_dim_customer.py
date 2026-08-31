from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

CUSTOMERS_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_customers_dataset.csv"
)

DIM_CUSTOMER_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "dim_customer.csv"
)


# ---------------------------------------------------------
# BUILD DIM CUSTOMER
# ---------------------------------------------------------

def build_dim_customer():
    """
    Build an analytics-ready customer dimension
    from the raw Olist customers dataset.
    """

    print("=" * 80)
    print("BUILDING DIM_CUSTOMER")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW CUSTOMER DATA
    # -----------------------------------------------------

    customers_df = pd.read_csv(
        CUSTOMERS_SOURCE_FILE
    )

    print(
        f"\nRaw customer rows: "
        f"{len(customers_df):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE SOURCE GRAIN
    # -----------------------------------------------------

    unique_customer_ids = (
        customers_df[
            "customer_id"
        ].nunique()
    )

    print(
        f"Unique customer IDs: "
        f"{unique_customer_ids:,}"
    )

    if (
        len(customers_df)
        != unique_customer_ids
    ):
        raise ValueError(
            "Customers source is not "
            "one row per customer_id."
        )

    # -----------------------------------------------------
    # 3. CHECK UNIQUE CUSTOMER IDENTITIES
    # -----------------------------------------------------

    unique_real_customers = (
        customers_df[
            "customer_unique_id"
        ].nunique()
    )

    print(
        f"Unique customer_unique_id values: "
        f"{unique_real_customers:,}"
    )

    repeat_customer_records = (
        customers_df[
            "customer_unique_id"
        ].duplicated(
            keep=False
        ).sum()
    )

    print(
        "Rows belonging to customers "
        f"with multiple records: "
        f"{repeat_customer_records:,}"
    )

    # -----------------------------------------------------
    # 4. STANDARDIZE TEXT FIELDS
    # -----------------------------------------------------

    customers_df[
        "customer_city"
    ] = (
        customers_df[
            "customer_city"
        ]
        .astype("string")
        .str.strip()
        .str.title()
    )

    customers_df[
        "customer_state"
    ] = (
        customers_df[
            "customer_state"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    # -----------------------------------------------------
    # 5. STANDARDIZE ZIP CODE PREFIX
    # -----------------------------------------------------

    customers_df[
        "customer_zip_code_prefix"
    ] = (
        customers_df[
            "customer_zip_code_prefix"
        ]
        .astype("string")
        .str.zfill(5)
    )

    # -----------------------------------------------------
    # 6. CREATE REPEAT-CUSTOMER INDICATOR
    # -----------------------------------------------------

    customer_record_counts = (
        customers_df
        .groupby(
            "customer_unique_id"
        )["customer_id"]
        .transform("count")
    )

    customers_df[
        "customer_record_count"
    ] = customer_record_counts

    customers_df[
        "is_repeat_customer"
    ] = (
        customers_df[
            "customer_record_count"
        ] > 1
    ).astype(int)

    # -----------------------------------------------------
    # 7. SELECT DIMENSION COLUMNS
    # -----------------------------------------------------

    dim_customer = customers_df[
        [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
            "customer_record_count",
            "is_repeat_customer",
        ]
    ].copy()

    # -----------------------------------------------------
    # 8. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(dim_customer)

    output_unique_customer_ids = (
        dim_customer[
            "customer_id"
        ].nunique()
    )

    print(
        f"\nProcessed rows: "
        f"{output_rows:,}"
    )

    print(
        "Processed unique customer IDs: "
        f"{output_unique_customer_ids:,}"
    )

    if (
        output_rows
        != len(customers_df)
    ):
        raise ValueError(
            "Row count changed during "
            "dim_customer transformation."
        )

    if (
        output_rows
        != output_unique_customer_ids
    ):
        raise ValueError(
            "dim_customer grain "
            "validation failed."
        )

    # -----------------------------------------------------
    # 9. DATA QUALITY CHECKS
    # -----------------------------------------------------

    print(
        "\nMissing values:"
    )

    print(
        dim_customer
        .isna()
        .sum()
    )

    print(
        "\nDuplicate customer IDs:"
    )

    print(
        dim_customer[
            "customer_id"
        ].duplicated().sum()
    )

    repeat_unique_customers = (
        dim_customer.loc[
            dim_customer[
                "is_repeat_customer"
            ] == 1,
            "customer_unique_id"
        ]
        .nunique()
    )

    print(
        "\nUnderlying customers with "
        "multiple customer records: "
        f"{repeat_unique_customers:,}"
    )

    # -----------------------------------------------------
    # 10. SAVE PROCESSED DIMENSION
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    dim_customer.to_csv(
        DIM_CUSTOMER_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved dim_customer to:"
    )

    print(
        DIM_CUSTOMER_OUTPUT_FILE
    )

    print(
        "\nDIM_CUSTOMER BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_dim_customer()