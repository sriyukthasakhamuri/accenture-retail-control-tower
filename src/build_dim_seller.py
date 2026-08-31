from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

SELLERS_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_sellers_dataset.csv"
)

DIM_SELLER_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "dim_seller.csv"
)


# ---------------------------------------------------------
# BUILD DIM SELLER
# ---------------------------------------------------------

def build_dim_seller():
    """
    Build an analytics-ready seller dimension
    from the raw Olist sellers dataset.
    """

    print("=" * 80)
    print("BUILDING DIM_SELLER")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW SELLER DATA
    # -----------------------------------------------------

    sellers_df = pd.read_csv(
        SELLERS_SOURCE_FILE
    )

    print(
        f"\nRaw seller rows: "
        f"{len(sellers_df):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE SOURCE GRAIN
    # -----------------------------------------------------

    unique_sellers = (
        sellers_df[
            "seller_id"
        ].nunique()
    )

    print(
        f"Unique seller IDs: "
        f"{unique_sellers:,}"
    )

    if (
        len(sellers_df)
        != unique_sellers
    ):
        raise ValueError(
            "Seller source is not "
            "one row per seller_id."
        )

    # -----------------------------------------------------
    # 3. CHECK MISSING VALUES
    # -----------------------------------------------------

    print(
        "\nMissing values in raw seller data:"
    )

    print(
        sellers_df
        .isna()
        .sum()
    )

    # -----------------------------------------------------
    # 4. STANDARDIZE CITY
    # -----------------------------------------------------

    sellers_df[
        "seller_city"
    ] = (
        sellers_df[
            "seller_city"
        ]
        .astype("string")
        .str.strip()
        .str.title()
    )

    # -----------------------------------------------------
    # 5. STANDARDIZE STATE
    # -----------------------------------------------------

    sellers_df[
        "seller_state"
    ] = (
        sellers_df[
            "seller_state"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    # -----------------------------------------------------
    # 6. STANDARDIZE ZIP CODE PREFIX
    # -----------------------------------------------------

    sellers_df[
        "seller_zip_code_prefix"
    ] = (
        sellers_df[
            "seller_zip_code_prefix"
        ]
        .astype("string")
        .str.zfill(5)
    )

    # -----------------------------------------------------
    # 7. SELECT DIMENSION COLUMNS
    # -----------------------------------------------------

    dim_seller = sellers_df[
        [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ]
    ].copy()

    # -----------------------------------------------------
    # 8. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(
        dim_seller
    )

    output_unique_sellers = (
        dim_seller[
            "seller_id"
        ].nunique()
    )

    print(
        f"\nProcessed seller rows: "
        f"{output_rows:,}"
    )

    print(
        f"Processed unique seller IDs: "
        f"{output_unique_sellers:,}"
    )

    if (
        output_rows
        != len(sellers_df)
    ):
        raise ValueError(
            "Row count changed during "
            "dim_seller transformation."
        )

    if (
        output_rows
        != output_unique_sellers
    ):
        raise ValueError(
            "dim_seller grain "
            "validation failed."
        )

    # -----------------------------------------------------
    # 9. QUALITY CHECKS
    # -----------------------------------------------------

    duplicate_seller_ids = (
        dim_seller[
            "seller_id"
        ]
        .duplicated()
        .sum()
    )

    print(
        "\nDuplicate seller IDs:"
    )

    print(
        duplicate_seller_ids
    )

    print(
        "\nMissing values in dim_seller:"
    )

    print(
        dim_seller
        .isna()
        .sum()
    )

    unique_states = (
        dim_seller[
            "seller_state"
        ].nunique()
    )

    print(
        "\nUnique seller states:"
    )

    print(
        unique_states
    )

    # -----------------------------------------------------
    # 10. SAVE PROCESSED DIMENSION
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    dim_seller.to_csv(
        DIM_SELLER_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved dim_seller to:"
    )

    print(
        DIM_SELLER_OUTPUT_FILE
    )

    print(
        "\nDIM_SELLER BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_dim_seller()