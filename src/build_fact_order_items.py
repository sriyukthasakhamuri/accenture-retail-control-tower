from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

ORDER_ITEMS_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_order_items_dataset.csv"
)

FACT_ORDER_ITEMS_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "fact_order_items.csv"
)

FACT_ORDERS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_orders.csv"
)

DIM_PRODUCT_FILE = (
    PROCESSED_DATA_PATH
    / "dim_product.csv"
)

DIM_SELLER_FILE = (
    PROCESSED_DATA_PATH
    / "dim_seller.csv"
)


# ---------------------------------------------------------
# BUILD FACT ORDER ITEMS
# ---------------------------------------------------------

def build_fact_order_items():
    """
    Build the analytics-ready sales transaction fact table.

    Grain:
    One row = one item position within an order.
    """

    print("=" * 80)
    print("BUILDING FACT_ORDER_ITEMS")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW ORDER ITEM DATA
    # -----------------------------------------------------

    order_items_df = pd.read_csv(
        ORDER_ITEMS_SOURCE_FILE
    )

    print(
        f"\nRaw order-item rows: "
        f"{len(order_items_df):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE COMPOSITE KEY / SOURCE GRAIN
    # -----------------------------------------------------

    unique_item_keys = (
        order_items_df[
            [
                "order_id",
                "order_item_id",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        "Unique order_id + order_item_id "
        f"combinations: {unique_item_keys:,}"
    )

    if (
        len(order_items_df)
        != unique_item_keys
    ):
        raise ValueError(
            "Order-items source does not have "
            "a unique order_id + order_item_id grain."
        )

    # -----------------------------------------------------
    # 3. CONVERT SHIPPING TIMESTAMP
    # -----------------------------------------------------

    order_items_df[
        "shipping_limit_date"
    ] = pd.to_datetime(
        order_items_df[
            "shipping_limit_date"
        ],
        errors="coerce"
    )

    # -----------------------------------------------------
    # 4. CHECK RAW NUMERIC FIELDS
    # -----------------------------------------------------

    print(
        "\nMissing price values:"
    )

    print(
        order_items_df[
            "price"
        ].isna().sum()
    )

    print(
        "Missing freight values:"
    )

    print(
        order_items_df[
            "freight_value"
        ].isna().sum()
    )

    # -----------------------------------------------------
    # 5. CREATE ITEM-LEVEL MEASURES
    # -----------------------------------------------------

    order_items_df[
        "item_total_value"
    ] = (
        order_items_df["price"]
        +
        order_items_df["freight_value"]
    )

    # Each row represents one item position.
    order_items_df[
        "item_quantity"
    ] = 1

    # -----------------------------------------------------
    # 6. SELECT FACT COLUMNS
    # -----------------------------------------------------

    fact_order_items = order_items_df[
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
            "item_total_value",
            "item_quantity",
        ]
    ].copy()

    # -----------------------------------------------------
    # 7. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(
        fact_order_items
    )

    output_unique_keys = (
        fact_order_items[
            [
                "order_id",
                "order_item_id",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        f"\nProcessed rows: "
        f"{output_rows:,}"
    )

    print(
        "Processed unique item keys: "
        f"{output_unique_keys:,}"
    )

    if (
        output_rows
        != len(order_items_df)
    ):
        raise ValueError(
            "fact_order_items row count "
            "changed during transformation."
        )

    if (
        output_rows
        != output_unique_keys
    ):
        raise ValueError(
            "fact_order_items grain "
            "validation failed."
        )

    # -----------------------------------------------------
    # 8. LOAD RELATED ANALYTICAL TABLES
    # -----------------------------------------------------

    fact_orders = pd.read_csv(
        FACT_ORDERS_FILE
    )

    dim_product = pd.read_csv(
        DIM_PRODUCT_FILE
    )

    dim_seller = pd.read_csv(
        DIM_SELLER_FILE
    )

    # -----------------------------------------------------
    # 9. VALIDATE ORDER RELATIONSHIP
    # -----------------------------------------------------

    order_item_order_ids = set(
        fact_order_items[
            "order_id"
        ].dropna()
    )

    valid_order_ids = set(
        fact_orders[
            "order_id"
        ].dropna()
    )

    missing_order_ids = (
        order_item_order_ids
        -
        valid_order_ids
    )

    print(
        "\nOrder IDs missing "
        "from fact_orders:"
    )

    print(
        len(missing_order_ids)
    )

    if missing_order_ids:
        raise ValueError(
            "Some order-item records do not "
            "match fact_orders."
        )

    # -----------------------------------------------------
    # 10. VALIDATE PRODUCT RELATIONSHIP
    # -----------------------------------------------------

    item_product_ids = set(
        fact_order_items[
            "product_id"
        ].dropna()
    )

    valid_product_ids = set(
        dim_product[
            "product_id"
        ].dropna()
    )

    missing_product_ids = (
        item_product_ids
        -
        valid_product_ids
    )

    print(
        "\nProduct IDs missing "
        "from dim_product:"
    )

    print(
        len(missing_product_ids)
    )

    if missing_product_ids:
        raise ValueError(
            "Some order-item products do not "
            "exist in dim_product."
        )

    # -----------------------------------------------------
    # 11. VALIDATE SELLER RELATIONSHIP
    # -----------------------------------------------------

    item_seller_ids = set(
        fact_order_items[
            "seller_id"
        ].dropna()
    )

    valid_seller_ids = set(
        dim_seller[
            "seller_id"
        ].dropna()
    )

    missing_seller_ids = (
        item_seller_ids
        -
        valid_seller_ids
    )

    print(
        "\nSeller IDs missing "
        "from dim_seller:"
    )

    print(
        len(missing_seller_ids)
    )

    if missing_seller_ids:
        raise ValueError(
            "Some order-item sellers do not "
            "exist in dim_seller."
        )

    # -----------------------------------------------------
    # 12. SALES SUMMARY
    # -----------------------------------------------------

    total_item_sales = (
        fact_order_items[
            "price"
        ].sum()
    )

    total_freight = (
        fact_order_items[
            "freight_value"
        ].sum()
    )

    total_transaction_value = (
        fact_order_items[
            "item_total_value"
        ].sum()
    )

    print(
        "\nTotal item sales value:"
    )

    print(
        f"{total_item_sales:,.2f}"
    )

    print(
        "Total freight value:"
    )

    print(
        f"{total_freight:,.2f}"
    )

    print(
        "Total item + freight value:"
    )

    print(
        f"{total_transaction_value:,.2f}"
    )

    # -----------------------------------------------------
    # 13. SAVE PROCESSED FACT
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    fact_order_items.to_csv(
        FACT_ORDER_ITEMS_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved fact_order_items to:"
    )

    print(
        FACT_ORDER_ITEMS_OUTPUT_FILE
    )

    print(
        "\nFACT_ORDER_ITEMS BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_fact_order_items()