from pathlib import Path

import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

RAW_DIR = Path("data/raw")
FIXTURE_DIR = Path("tests/fixtures/raw")

SAMPLE_ORDER_COUNT = 500
RANDOM_STATE = 42


# =========================================================
# FILE NAMES
# =========================================================

CUSTOMERS_FILE = "olist_customers_dataset.csv"
GEOLOCATION_FILE = "olist_geolocation_dataset.csv"
ORDER_ITEMS_FILE = "olist_order_items_dataset.csv"
PAYMENTS_FILE = "olist_order_payments_dataset.csv"
REVIEWS_FILE = "olist_order_reviews_dataset.csv"
ORDERS_FILE = "olist_orders_dataset.csv"
PRODUCTS_FILE = "olist_products_dataset.csv"
SELLERS_FILE = "olist_sellers_dataset.csv"
TRANSLATION_FILE = "product_category_name_translation.csv"


def load_csv(filename):
    """Load a raw Olist CSV file."""

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required raw file not found: {path}"
        )

    return pd.read_csv(path)


def save_fixture(dataframe, filename):
    """Save a dataframe to the CI fixture directory."""

    output_path = FIXTURE_DIR / filename

    dataframe.to_csv(
        output_path,
        index=False,
    )

    print(
        f"{filename}: "
        f"{len(dataframe):,} rows"
    )


def main():
    print("=" * 70)
    print("CREATING CI FIXTURE DATASET")
    print("=" * 70)

    FIXTURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # 1. LOAD CORE DATASETS
    # -----------------------------------------------------

    orders = load_csv(ORDERS_FILE)
    customers = load_csv(CUSTOMERS_FILE)
    order_items = load_csv(ORDER_ITEMS_FILE)
    payments = load_csv(PAYMENTS_FILE)
    reviews = load_csv(REVIEWS_FILE)
    products = load_csv(PRODUCTS_FILE)
    sellers = load_csv(SELLERS_FILE)
    geolocation = load_csv(GEOLOCATION_FILE)
    translation = load_csv(TRANSLATION_FILE)

    # -----------------------------------------------------
    # 2. SAMPLE ORDERS
    # -----------------------------------------------------

    sample_size = min(
        SAMPLE_ORDER_COUNT,
        len(orders),
    )

    sampled_orders = (
        orders.sample(
            n=sample_size,
            random_state=RANDOM_STATE,
        )
        .sort_values("order_purchase_timestamp")
        .reset_index(drop=True)
    )

    sampled_order_ids = set(
        sampled_orders["order_id"]
    )

    sampled_customer_ids = set(
        sampled_orders["customer_id"]
    )

    # -----------------------------------------------------
    # 3. FILTER ORDER-LEVEL CHILD TABLES
    # -----------------------------------------------------

    sampled_order_items = order_items[
        order_items["order_id"].isin(
            sampled_order_ids
        )
    ].copy()

    sampled_payments = payments[
        payments["order_id"].isin(
            sampled_order_ids
        )
    ].copy()

    sampled_reviews = reviews[
        reviews["order_id"].isin(
            sampled_order_ids
        )
    ].copy()

    # -----------------------------------------------------
    # 4. FILTER CUSTOMERS
    # -----------------------------------------------------

    sampled_customers = customers[
        customers["customer_id"].isin(
            sampled_customer_ids
        )
    ].copy()

    # -----------------------------------------------------
    # 5. FILTER PRODUCTS
    # -----------------------------------------------------

    sampled_product_ids = set(
        sampled_order_items["product_id"]
    )

    sampled_products = products[
        products["product_id"].isin(
            sampled_product_ids
        )
    ].copy()

    # -----------------------------------------------------
    # 6. FILTER SELLERS
    # -----------------------------------------------------

    sampled_seller_ids = set(
        sampled_order_items["seller_id"]
    )

    sampled_sellers = sellers[
        sellers["seller_id"].isin(
            sampled_seller_ids
        )
    ].copy()

    # -----------------------------------------------------
    # 7. FILTER GEOLOCATION
    # -----------------------------------------------------

    customer_zip_codes = set(
        sampled_customers[
            "customer_zip_code_prefix"
        ].dropna()
    )

    seller_zip_codes = set(
        sampled_sellers[
            "seller_zip_code_prefix"
        ].dropna()
    )

    required_zip_codes = (
        customer_zip_codes
        | seller_zip_codes
    )

    sampled_geolocation = geolocation[
        geolocation[
            "geolocation_zip_code_prefix"
        ].isin(required_zip_codes)
    ].copy()

    # -----------------------------------------------------
    # 8. FILTER CATEGORY TRANSLATIONS
    # -----------------------------------------------------

    required_categories = set(
        sampled_products[
            "product_category_name"
        ].dropna()
    )

    sampled_translation = translation[
        translation[
            "product_category_name"
        ].isin(required_categories)
    ].copy()

    # -----------------------------------------------------
    # 9. RELATIONSHIP VALIDATION
    # -----------------------------------------------------

    missing_customers = (
        sampled_order_ids
        and (
            set(sampled_orders["customer_id"])
            - set(sampled_customers["customer_id"])
        )
    )

    missing_products = (
        set(sampled_order_items["product_id"])
        - set(sampled_products["product_id"])
    )

    missing_sellers = (
        set(sampled_order_items["seller_id"])
        - set(sampled_sellers["seller_id"])
    )

    if missing_customers:
        raise ValueError(
            "CI fixture contains orders with "
            "missing customers."
        )

    if missing_products:
        raise ValueError(
            "CI fixture contains order items with "
            "missing products."
        )

    if missing_sellers:
        raise ValueError(
            "CI fixture contains order items with "
            "missing sellers."
        )

    # -----------------------------------------------------
    # 10. SAVE FIXTURE FILES
    # -----------------------------------------------------

    print("\nSaving fixture files...\n")

    save_fixture(
        sampled_customers,
        CUSTOMERS_FILE,
    )

    save_fixture(
        sampled_geolocation,
        GEOLOCATION_FILE,
    )

    save_fixture(
        sampled_order_items,
        ORDER_ITEMS_FILE,
    )

    save_fixture(
        sampled_payments,
        PAYMENTS_FILE,
    )

    save_fixture(
        sampled_reviews,
        REVIEWS_FILE,
    )

    save_fixture(
        sampled_orders,
        ORDERS_FILE,
    )

    save_fixture(
        sampled_products,
        PRODUCTS_FILE,
    )

    save_fixture(
        sampled_sellers,
        SELLERS_FILE,
    )

    save_fixture(
        sampled_translation,
        TRANSLATION_FILE,
    )

    print("\n" + "=" * 70)
    print("CI FIXTURE CREATION COMPLETE")
    print("=" * 70)

    print(
        f"\nSampled orders: "
        f"{len(sampled_orders):,}"
    )

    print(
        f"Fixture directory: "
        f"{FIXTURE_DIR}"
    )


if __name__ == "__main__":
    main()