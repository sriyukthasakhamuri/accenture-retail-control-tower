from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

PRODUCTS_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_products_dataset.csv"
)

CATEGORY_TRANSLATION_FILE = (
    RAW_DATA_PATH
    / "product_category_name_translation.csv"
)

DIM_PRODUCT_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "dim_product.csv"
)


# ---------------------------------------------------------
# BUILD DIM PRODUCT
# ---------------------------------------------------------

def build_dim_product():
    """
    Build an analytics-ready product dimension by
    combining product attributes with English
    category translations.
    """

    print("=" * 80)
    print("BUILDING DIM_PRODUCT")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW SOURCE DATA
    # -----------------------------------------------------

    products_df = pd.read_csv(
        PRODUCTS_SOURCE_FILE
    )

    translation_df = pd.read_csv(
        CATEGORY_TRANSLATION_FILE
    )

    print(
        f"\nRaw product rows: "
        f"{len(products_df):,}"
    )

    print(
        "Category translation rows: "
        f"{len(translation_df):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE PRODUCT GRAIN
    # -----------------------------------------------------

    unique_products = (
        products_df["product_id"].nunique()
    )

    print(
        f"Unique product IDs: "
        f"{unique_products:,}"
    )

    if len(products_df) != unique_products:
        raise ValueError(
            "Products source is not "
            "one row per product_id."
        )

    # -----------------------------------------------------
    # 3. VALIDATE TRANSLATION LOOKUP KEY
    # -----------------------------------------------------

    duplicate_translation_keys = (
        translation_df[
            "product_category_name"
        ]
        .duplicated()
        .sum()
    )

    print(
        "\nDuplicate category keys "
        "in translation table:"
    )

    print(
        duplicate_translation_keys
    )

    if duplicate_translation_keys != 0:
        raise ValueError(
            "Category translation key "
            "is not unique."
        )

    # -----------------------------------------------------
    # 4. RENAME MISSPELLED SOURCE COLUMNS
    # -----------------------------------------------------

    products_df = products_df.rename(
        columns={
            "product_name_lenght":
                "product_name_length",
            "product_description_lenght":
                "product_description_length",
        }
    )

    # -----------------------------------------------------
    # 5. LEFT JOIN CATEGORY TRANSLATION
    # -----------------------------------------------------

    products_enriched = products_df.merge(
        translation_df,
        on="product_category_name",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    # -----------------------------------------------------
    # 6. VALIDATE JOIN ROW COUNT
    # -----------------------------------------------------

    print(
        "\nRows before translation join:"
    )

    print(
        f"{len(products_df):,}"
    )

    print(
        "Rows after translation join:"
    )

    print(
        f"{len(products_enriched):,}"
    )

    if (
        len(products_enriched)
        != len(products_df)
    ):
        raise ValueError(
            "Product translation join "
            "changed the product row count."
        )

    # -----------------------------------------------------
    # 7. CHECK TRANSLATION MATCHES
    # -----------------------------------------------------

    print(
        "\nTranslation join results:"
    )

    print(
        products_enriched[
            "_merge"
        ].value_counts()
    )

    products_without_translation = (
        products_enriched.loc[
            products_enriched[
                "product_category_name"
            ].notna()
            &
            products_enriched[
                "product_category_name_english"
            ].isna()
        ]
    )

    print(
        "\nProducts with a source category "
        "but no English translation:"
    )

    print(
        f"{len(products_without_translation):,}"
    )

    # -----------------------------------------------------
    # 8. CHECK MISSING PRODUCT ATTRIBUTES
    # -----------------------------------------------------

    print(
        "\nMissing product attributes:"
    )

    product_missing_values = (
        products_enriched[
            [
                "product_category_name",
                "product_category_name_english",
                "product_name_length",
                "product_description_length",
                "product_photos_qty",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ]
        ]
        .isna()
        .sum()
    )

    print(
        product_missing_values
    )

    # -----------------------------------------------------
    # 9. CREATE DATA QUALITY FLAGS
    # -----------------------------------------------------

    products_enriched[
        "has_product_category"
    ] = (
        products_enriched[
            "product_category_name"
        ]
        .notna()
        .astype(int)
    )

    products_enriched[
        "has_english_category"
    ] = (
        products_enriched[
            "product_category_name_english"
        ]
        .notna()
        .astype(int)
    )

    products_enriched[
        "has_complete_dimensions"
    ] = (
        products_enriched[
            [
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ]
        ]
        .notna()
        .all(axis=1)
        .astype(int)
    )

    # -----------------------------------------------------
    # 10. REMOVE MERGE HELPER COLUMN
    # -----------------------------------------------------

    products_enriched = (
        products_enriched
        .drop(columns=["_merge"])
    )

    # -----------------------------------------------------
    # 11. SELECT DIMENSION COLUMNS
    # -----------------------------------------------------

    dim_product = products_enriched[
        [
            "product_id",
            "product_category_name",
            "product_category_name_english",
            "product_name_length",
            "product_description_length",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
            "has_product_category",
            "has_english_category",
            "has_complete_dimensions",
        ]
    ].copy()

    # -----------------------------------------------------
    # 12. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(dim_product)

    output_unique_products = (
        dim_product[
            "product_id"
        ].nunique()
    )

    print(
        f"\nProcessed product rows: "
        f"{output_rows:,}"
    )

    print(
        "Processed unique product IDs: "
        f"{output_unique_products:,}"
    )

    if (
        output_rows
        != len(products_df)
    ):
        raise ValueError(
            "Row count changed during "
            "dim_product transformation."
        )

    if (
        output_rows
        != output_unique_products
    ):
        raise ValueError(
            "dim_product grain "
            "validation failed."
        )

    # -----------------------------------------------------
    # 13. SUMMARY
    # -----------------------------------------------------

    print(
        "\nProducts with categories:"
    )

    print(
        f"{dim_product['has_product_category'].sum():,}"
    )

    print(
        "Products with English categories:"
    )

    print(
        f"{dim_product['has_english_category'].sum():,}"
    )

    print(
        "Products with complete "
        "physical dimensions:"
    )

    print(
        f"{dim_product['has_complete_dimensions'].sum():,}"
    )

    # -----------------------------------------------------
    # 14. SAVE PROCESSED DIMENSION
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    dim_product.to_csv(
        DIM_PRODUCT_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved dim_product to:"
    )

    print(
        DIM_PRODUCT_OUTPUT_FILE
    )

    print(
        "\nDIM_PRODUCT BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_dim_product()