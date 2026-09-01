from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

GEOLOCATION_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_geolocation_dataset.csv"
)

DIM_CUSTOMER_FILE = (
    PROCESSED_DATA_PATH
    / "dim_customer.csv"
)

DIM_SELLER_FILE = (
    PROCESSED_DATA_PATH
    / "dim_seller.csv"
)

DIM_GEOGRAPHY_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "dim_geography.csv"
)


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def most_common_value(series):
    """
    Return the most frequently occurring non-null value
    from a pandas Series.

    If all values are null, return pandas NA.
    """

    non_null_values = (
        series
        .dropna()
    )

    if non_null_values.empty:
        return pd.NA

    modes = (
        non_null_values
        .mode()
    )

    return modes.iloc[0]


# ---------------------------------------------------------
# BUILD DIM GEOGRAPHY
# ---------------------------------------------------------

def build_dim_geography():
    """
    Build an analytics-ready geography dimension
    from the raw Olist geolocation dataset.

    Grain:
    One row = one ZIP code prefix.
    """

    print("=" * 80)
    print("BUILDING DIM_GEOGRAPHY")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW GEOLOCATION DATA
    # -----------------------------------------------------

    geolocation_df = pd.read_csv(
        GEOLOCATION_SOURCE_FILE
    )

    print(
        f"\nRaw geolocation rows: "
        f"{len(geolocation_df):,}"
    )

    # -----------------------------------------------------
    # 2. CHECK RAW DUPLICATES
    # -----------------------------------------------------

    exact_duplicate_rows = (
        geolocation_df
        .duplicated()
        .sum()
    )

    print(
        "\nExact duplicate geolocation rows:"
    )

    print(
        f"{exact_duplicate_rows:,}"
    )

    # -----------------------------------------------------
    # 3. STANDARDIZE ZIP PREFIX
    # -----------------------------------------------------

    geolocation_df[
        "geolocation_zip_code_prefix"
    ] = (
        geolocation_df[
            "geolocation_zip_code_prefix"
        ]
        .astype("string")
        .str.zfill(5)
    )

    # -----------------------------------------------------
    # 4. STANDARDIZE CITY / STATE
    # -----------------------------------------------------

    geolocation_df[
        "geolocation_city"
    ] = (
        geolocation_df[
            "geolocation_city"
        ]
        .astype("string")
        .str.strip()
        .str.title()
    )

    geolocation_df[
        "geolocation_state"
    ] = (
        geolocation_df[
            "geolocation_state"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    # -----------------------------------------------------
    # 5. REMOVE EXACT DUPLICATES
    # -----------------------------------------------------

    geolocation_clean = (
        geolocation_df
        .drop_duplicates()
        .copy()
    )

    print(
        "\nRows after removing exact duplicates:"
    )

    print(
        f"{len(geolocation_clean):,}"
    )

    # -----------------------------------------------------
    # 6. PROFILE ZIP CODE GRAIN
    # -----------------------------------------------------

    unique_zip_prefixes = (
        geolocation_clean[
            "geolocation_zip_code_prefix"
        ]
        .nunique()
    )

    print(
        "\nUnique ZIP code prefixes:"
    )

    print(
        f"{unique_zip_prefixes:,}"
    )

    # -----------------------------------------------------
    # 7. CHECK LOCATION VARIATION PER ZIP
    # -----------------------------------------------------

    zip_quality = (
        geolocation_clean
        .groupby(
            "geolocation_zip_code_prefix",
            as_index=False
        )
        .agg(
            geolocation_observation_count=(
                "geolocation_lat",
                "size"
            ),
            unique_city_count=(
                "geolocation_city",
                "nunique"
            ),
            unique_state_count=(
                "geolocation_state",
                "nunique"
            ),
        )
    )

    zip_quality[
        "has_city_conflict"
    ] = (
        zip_quality[
            "unique_city_count"
        ] > 1
    ).astype(int)

    zip_quality[
        "has_state_conflict"
    ] = (
        zip_quality[
            "unique_state_count"
        ] > 1
    ).astype(int)

    print(
        "\nZIP prefixes linked to "
        "multiple city labels:"
    )

    print(
        f"{zip_quality['has_city_conflict'].sum():,}"
    )

    print(
        "\nZIP prefixes linked to "
        "multiple state labels:"
    )

    print(
        f"{zip_quality['has_state_conflict'].sum():,}"
    )

    # -----------------------------------------------------
    # 8. AGGREGATE TO ONE ROW PER ZIP PREFIX
    # -----------------------------------------------------

    geography_core = (
        geolocation_clean
        .groupby(
            "geolocation_zip_code_prefix",
            as_index=False
        )
        .agg(
            latitude=(
                "geolocation_lat",
                "median"
            ),
            longitude=(
                "geolocation_lng",
                "median"
            ),
            city=(
                "geolocation_city",
                most_common_value
            ),
            state=(
                "geolocation_state",
                most_common_value
            ),
        )
    )

    # -----------------------------------------------------
    # 9. ADD DATA QUALITY INFORMATION
    # -----------------------------------------------------

    dim_geography = (
        geography_core
        .merge(
            zip_quality,
            on="geolocation_zip_code_prefix",
            how="left",
            validate="one_to_one"
        )
    )

    # -----------------------------------------------------
    # 10. RENAME BUSINESS KEY
    # -----------------------------------------------------

    dim_geography = (
        dim_geography
        .rename(
            columns={
                "geolocation_zip_code_prefix":
                    "zip_code_prefix"
            }
        )
    )

    # -----------------------------------------------------
    # 11. CREATE GEOGRAPHY KEY
    # -----------------------------------------------------

    dim_geography[
        "geography_key"
    ] = (
        dim_geography[
            "zip_code_prefix"
        ]
    )

    # -----------------------------------------------------
    # 12. SELECT FINAL COLUMN ORDER
    # -----------------------------------------------------

    dim_geography = dim_geography[
        [
            "geography_key",
            "zip_code_prefix",
            "city",
            "state",
            "latitude",
            "longitude",
            "geolocation_observation_count",
            "unique_city_count",
            "unique_state_count",
            "has_city_conflict",
            "has_state_conflict",
        ]
    ].copy()

    # -----------------------------------------------------
    # 13. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(
        dim_geography
    )

    output_unique_zips = (
        dim_geography[
            "zip_code_prefix"
        ]
        .nunique()
    )

    duplicate_geography_keys = (
        dim_geography[
            "geography_key"
        ]
        .duplicated()
        .sum()
    )

    print(
        "\nProcessed geography rows:"
    )

    print(
        f"{output_rows:,}"
    )

    print(
        "\nProcessed unique ZIP prefixes:"
    )

    print(
        f"{output_unique_zips:,}"
    )

    print(
        "\nDuplicate geography keys:"
    )

    print(
        duplicate_geography_keys
    )

    if (
        output_rows
        != output_unique_zips
    ):
        raise ValueError(
            "dim_geography is not "
            "one row per ZIP prefix."
        )

    if duplicate_geography_keys != 0:
        raise ValueError(
            "dim_geography contains "
            "duplicate geography keys."
        )

    # -----------------------------------------------------
    # 14. CHECK MISSING GEOGRAPHY VALUES
    # -----------------------------------------------------

    print(
        "\nMissing geography values:"
    )

    print(
        dim_geography[
            [
                "zip_code_prefix",
                "city",
                "state",
                "latitude",
                "longitude",
            ]
        ]
        .isna()
        .sum()
    )

    # -----------------------------------------------------
    # 15. VALIDATE CUSTOMER ZIP COVERAGE
    # -----------------------------------------------------

    dim_customer = pd.read_csv(
        DIM_CUSTOMER_FILE,
        dtype={
            "customer_zip_code_prefix":
                "string"
        }
    )

    dim_customer[
        "customer_zip_code_prefix"
    ] = (
        dim_customer[
            "customer_zip_code_prefix"
        ]
        .str.zfill(5)
    )

    geography_zip_codes = set(
        dim_geography[
            "zip_code_prefix"
        ].dropna()
    )

    customer_zip_codes = set(
        dim_customer[
            "customer_zip_code_prefix"
        ].dropna()
    )

    missing_customer_zip_codes = (
        customer_zip_codes
        -
        geography_zip_codes
    )

    print(
        "\nCustomer ZIP prefixes missing "
        "from dim_geography:"
    )

    print(
        f"{len(missing_customer_zip_codes):,}"
    )

    # -----------------------------------------------------
    # 16. VALIDATE SELLER ZIP COVERAGE
    # -----------------------------------------------------

    dim_seller = pd.read_csv(
        DIM_SELLER_FILE,
        dtype={
            "seller_zip_code_prefix":
                "string"
        }
    )

    dim_seller[
        "seller_zip_code_prefix"
    ] = (
        dim_seller[
            "seller_zip_code_prefix"
        ]
        .str.zfill(5)
    )

    seller_zip_codes = set(
        dim_seller[
            "seller_zip_code_prefix"
        ].dropna()
    )

    missing_seller_zip_codes = (
        seller_zip_codes
        -
        geography_zip_codes
    )

    print(
        "\nSeller ZIP prefixes missing "
        "from dim_geography:"
    )

    print(
        f"{len(missing_seller_zip_codes):,}"
    )

    # -----------------------------------------------------
    # 17. STATE SUMMARY
    # -----------------------------------------------------

    print(
        "\nGeography rows by state:"
    )

    print(
        dim_geography[
            "state"
        ]
        .value_counts()
        .sort_index()
    )

    # -----------------------------------------------------
    # 18. SAVE PROCESSED DIMENSION
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    dim_geography.to_csv(
        DIM_GEOGRAPHY_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved dim_geography to:"
    )

    print(
        DIM_GEOGRAPHY_OUTPUT_FILE
    )

    print(
        "\nDIM_GEOGRAPHY BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_dim_geography()