from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROCESSED_DATA_PATH = Path("data/processed")

FACT_ORDER_ITEMS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_order_items.csv"
)

FACT_PAYMENTS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_payments.csv"
)

FACT_ORDERS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_orders.csv"
)


# ---------------------------------------------------------
# RECONCILE FINANCIAL FACT TABLES
# ---------------------------------------------------------

def reconcile_order_financials():

    print("=" * 80)
    print("ORDER-LEVEL FINANCIAL RECONCILIATION")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. LOAD FACT TABLES
    # -----------------------------------------------------

    order_items = pd.read_csv(
        FACT_ORDER_ITEMS_FILE
    )

    payments = pd.read_csv(
        FACT_PAYMENTS_FILE
    )

    orders = pd.read_csv(
        FACT_ORDERS_FILE
    )

    # -----------------------------------------------------
    # 2. AGGREGATE ORDER ITEMS TO ORDER GRAIN
    # -----------------------------------------------------

    item_totals = (
        order_items
        .groupby(
            "order_id",
            as_index=False
        )
        .agg(
            merchandise_value=(
                "price",
                "sum"
            ),
            freight_value=(
                "freight_value",
                "sum"
            ),
            item_total_value=(
                "item_total_value",
                "sum"
            ),
            item_count=(
                "item_quantity",
                "sum"
            ),
        )
    )

    # -----------------------------------------------------
    # 3. AGGREGATE PAYMENTS TO ORDER GRAIN
    # -----------------------------------------------------

    payment_totals = (
        payments
        .groupby(
            "order_id",
            as_index=False
        )
        .agg(
            payment_value=(
                "payment_value",
                "sum"
            ),
            payment_record_count=(
                "payment_sequential",
                "count"
            ),
        )
    )

    # -----------------------------------------------------
    # 4. DISPLAY ORDER COVERAGE
    # -----------------------------------------------------

    print(
        "\nOrders represented in "
        "fact_order_items:"
    )

    print(
        f"{item_totals['order_id'].nunique():,}"
    )

    print(
        "\nOrders represented in "
        "fact_payments:"
    )

    print(
        f"{payment_totals['order_id'].nunique():,}"
    )

    # -----------------------------------------------------
    # 5. FULL OUTER JOIN
    # -----------------------------------------------------

    reconciliation = (
        item_totals.merge(
            payment_totals,
            on="order_id",
            how="outer",
            indicator=True,
            validate="one_to_one"
        )
    )

    print(
        "\nOrder coverage comparison:"
    )

    print(
        reconciliation[
            "_merge"
        ].value_counts()
    )

    # -----------------------------------------------------
    # 6. IDENTIFY ORDERS MISSING FROM EACH FACT
    # -----------------------------------------------------

    payment_only_orders = (
        reconciliation[
            "_merge"
        ].eq("right_only")
        .sum()
    )

    item_only_orders = (
        reconciliation[
            "_merge"
        ].eq("left_only")
        .sum()
    )

    print(
        "\nOrders with payments "
        "but no order items:"
    )

    print(
        f"{payment_only_orders:,}"
    )

    print(
        "\nOrders with order items "
        "but no payments:"
    )

    print(
        f"{item_only_orders:,}"
    )

    # -----------------------------------------------------
    # 7. COMPARE MATCHED ORDERS
    # -----------------------------------------------------

    matched = (
        reconciliation[
            reconciliation[
                "_merge"
            ].eq("both")
        ]
        .copy()
    )

    matched[
        "financial_difference"
    ] = (
        matched[
            "payment_value"
        ]
        -
        matched[
            "item_total_value"
        ]
    )

    matched[
        "absolute_difference"
    ] = (
        matched[
            "financial_difference"
        ].abs()
    )

    # Small tolerance for decimal / rounding effects
    tolerance = 0.01

    matched[
        "is_reconciled"
    ] = (
        matched[
            "absolute_difference"
        ] <= tolerance
    ).astype(int)

    reconciled_orders = (
        matched[
            "is_reconciled"
        ].sum()
    )

    unreconciled_orders = (
        len(matched)
        -
        reconciled_orders
    )

    print(
        "\nMatched orders:"
    )

    print(
        f"{len(matched):,}"
    )

    print(
        "\nOrders reconciling "
        "within $0.01:"
    )

    print(
        f"{reconciled_orders:,}"
    )

    print(
        "\nMatched orders with "
        "financial differences:"
    )

    print(
        f"{unreconciled_orders:,}"
    )

    # -----------------------------------------------------
    # 8. OVERALL FINANCIAL TOTALS
    # -----------------------------------------------------

    total_item_value = (
        order_items[
            "item_total_value"
        ].sum()
    )

    total_payment_value = (
        payments[
            "payment_value"
        ].sum()
    )

    total_difference = (
        total_payment_value
        -
        total_item_value
    )

    print(
        "\nTotal item + freight value:"
    )

    print(
        f"{total_item_value:,.2f}"
    )

    print(
        "\nTotal payment value:"
    )

    print(
        f"{total_payment_value:,.2f}"
    )

    print(
        "\nOverall difference:"
    )

    print(
        f"{total_difference:,.2f}"
    )

    # -----------------------------------------------------
    # 9. INVESTIGATE PAYMENT-ONLY ORDERS BY STATUS
    # -----------------------------------------------------

    payment_only = (
        reconciliation[
            reconciliation[
                "_merge"
            ].eq("right_only")
        ][
            [
                "order_id",
                "payment_value",
            ]
        ]
    )

    payment_only_with_status = (
        payment_only.merge(
            orders[
                [
                    "order_id",
                    "order_status",
                ]
            ],
            on="order_id",
            how="left",
            validate="one_to_one"
        )
    )

    print(
        "\nStatuses of orders with "
        "payments but no order items:"
    )

    print(
        payment_only_with_status[
            "order_status"
        ].value_counts(
            dropna=False
        )
    )

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    print(
        "\nFINANCIAL RECONCILIATION COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    reconcile_order_financials()