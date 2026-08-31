from pathlib import Path

import pandas as pd


RAW_DATA_PATH = Path("data/raw")


def check_key(df, columns, label):
    """
    Check whether one or more columns uniquely identify rows.
    """

    total_rows = len(df)

    unique_rows = (
        df[columns]
        .drop_duplicates()
        .shape[0]
    )

    duplicate_key_rows = (
        df.duplicated(
            subset=columns,
            keep=False
        ).sum()
    )

    print(f"\nCandidate key: {label}")
    print(f"Total rows: {total_rows:,}")
    print(f"Unique key combinations: {unique_rows:,}")
    print(
        f"Rows involved in duplicate keys: "
        f"{duplicate_key_rows:,}"
    )

    if total_rows == unique_rows:
        print("RESULT: Candidate key is UNIQUE.")
    else:
        print("RESULT: Candidate key is NOT unique.")


def analyze_customers():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_customers_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("CUSTOMERS")
    print("=" * 80)

    check_key(
        df,
        ["customer_id"],
        "customer_id"
    )

    print(
        "\nUnique customer_unique_id values:"
    )

    print(
        df["customer_unique_id"].nunique()
    )


def analyze_orders():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_orders_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("ORDERS")
    print("=" * 80)

    check_key(
        df,
        ["order_id"],
        "order_id"
    )


def analyze_order_items():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_order_items_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("ORDER ITEMS")
    print("=" * 80)

    check_key(
        df,
        ["order_id"],
        "order_id"
    )

    check_key(
        df,
        ["order_id", "order_item_id"],
        "order_id + order_item_id"
    )



def analyze_payments():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_order_payments_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("PAYMENTS")
    print("=" * 80)

    check_key(
        df,
        ["order_id"],
        "order_id"
    )

    check_key(
        df,
        ["order_id", "payment_sequential"],
        "order_id + payment_sequential"
    )


def analyze_reviews():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_order_reviews_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("REVIEWS")
    print("=" * 80)

    check_key(
        df,
        ["review_id"],
        "review_id"
    )

    check_key(
        df,
        ["order_id"],
        "order_id"
    )
    check_key(
        df,
        ["review_id", "order_id"],
        "review_id + order_id"
    )

def analyze_products():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_products_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("PRODUCTS")
    print("=" * 80)

    check_key(
        df,
        ["product_id"],
        "product_id"
    )


def analyze_sellers():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_sellers_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("SELLERS")
    print("=" * 80)

    check_key(
        df,
        ["seller_id"],
        "seller_id"
    )


def analyze_geolocation():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "olist_geolocation_dataset.csv"
    )

    print("\n" + "=" * 80)
    print("GEOLOCATION")
    print("=" * 80)

    print(
        f"Total rows: {len(df):,}"
    )

    print(
        "Unique zip code prefixes: "
        f"{df['geolocation_zip_code_prefix'].nunique():,}"
    )

    print(
        "Exact duplicate rows: "
        f"{df.duplicated().sum():,}"
    )


def analyze_translation():
    df = pd.read_csv(
        RAW_DATA_PATH /
        "product_category_name_translation.csv"
    )

    print("\n" + "=" * 80)
    print("CATEGORY TRANSLATION")
    print("=" * 80)

    check_key(
        df,
        ["product_category_name"],
        "product_category_name"
    )


if __name__ == "__main__":

    analyze_customers()
    analyze_orders()
    analyze_order_items()
    analyze_payments()
    analyze_reviews()
    analyze_products()
    analyze_sellers()
    analyze_geolocation()
    analyze_translation()