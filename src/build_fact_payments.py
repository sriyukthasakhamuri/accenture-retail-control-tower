from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

PAYMENTS_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_order_payments_dataset.csv"
)

FACT_PAYMENTS_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "fact_payments.csv"
)

FACT_ORDERS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_orders.csv"
)


# ---------------------------------------------------------
# BUILD FACT PAYMENTS
# ---------------------------------------------------------

def build_fact_payments():
    """
    Build an analytics-ready payment fact table.

    Grain:
    One row = one payment sequence associated
    with an order.
    """

    print("=" * 80)
    print("BUILDING FACT_PAYMENTS")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW PAYMENT DATA
    # -----------------------------------------------------

    payments_df = pd.read_csv(
        PAYMENTS_SOURCE_FILE
    )

    print(
        f"\nRaw payment rows: "
        f"{len(payments_df):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE COMPOSITE KEY
    # -----------------------------------------------------

    unique_payment_keys = (
        payments_df[
            [
                "order_id",
                "payment_sequential",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        "Unique order_id + payment_sequential "
        f"combinations: {unique_payment_keys:,}"
    )

    if (
        len(payments_df)
        != unique_payment_keys
    ):
        raise ValueError(
            "Payment source does not have a "
            "unique order_id + payment_sequential grain."
        )

    # -----------------------------------------------------
    # 3. CHECK MISSING VALUES
    # -----------------------------------------------------

    print(
        "\nMissing values:"
    )

    print(
        payments_df
        .isna()
        .sum()
    )

    # -----------------------------------------------------
    # 4. CHECK PAYMENT VALUE QUALITY
    # -----------------------------------------------------

    negative_payment_values = (
        payments_df[
            "payment_value"
        ] < 0
    ).sum()

    print(
        "\nNegative payment values:"
    )

    print(
        negative_payment_values
    )

    # -----------------------------------------------------
    # 5. CREATE PAYMENT FLAGS
    # -----------------------------------------------------

    payments_df[
        "is_credit_card"
    ] = (
        payments_df[
            "payment_type"
        ]
        .eq("credit_card")
        .astype(int)
    )

    payments_df[
        "is_voucher"
    ] = (
        payments_df[
            "payment_type"
        ]
        .eq("voucher")
        .astype(int)
    )

    payments_df[
        "is_debit_card"
    ] = (
        payments_df[
            "payment_type"
        ]
        .eq("debit_card")
        .astype(int)
    )

    payments_df[
        "is_boleto"
    ] = (
        payments_df[
            "payment_type"
        ]
        .eq("boleto")
        .astype(int)
    )

    # -----------------------------------------------------
    # 6. CREATE INSTALLMENT INDICATORS
    # -----------------------------------------------------

    payments_df[
        "is_installment_payment"
    ] = (
        payments_df[
            "payment_installments"
        ] > 1
    ).astype(int)

    # -----------------------------------------------------
    # 7. SELECT FACT TABLE COLUMNS
    # -----------------------------------------------------

    fact_payments = payments_df[
        [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
            "is_credit_card",
            "is_voucher",
            "is_debit_card",
            "is_boleto",
            "is_installment_payment",
        ]
    ].copy()

    # -----------------------------------------------------
    # 8. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(
        fact_payments
    )

    output_unique_keys = (
        fact_payments[
            [
                "order_id",
                "payment_sequential",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        f"\nProcessed payment rows: "
        f"{output_rows:,}"
    )

    print(
        "Processed unique payment keys: "
        f"{output_unique_keys:,}"
    )

    if (
        output_rows
        != len(payments_df)
    ):
        raise ValueError(
            "fact_payments row count changed "
            "during transformation."
        )

    if (
        output_rows
        != output_unique_keys
    ):
        raise ValueError(
            "fact_payments grain "
            "validation failed."
        )

    # -----------------------------------------------------
    # 9. VALIDATE RELATIONSHIP TO FACT_ORDERS
    # -----------------------------------------------------

    fact_orders = pd.read_csv(
        FACT_ORDERS_FILE
    )

    payment_order_ids = set(
        fact_payments[
            "order_id"
        ].dropna()
    )

    valid_order_ids = set(
        fact_orders[
            "order_id"
        ].dropna()
    )

    missing_order_ids = (
        payment_order_ids
        -
        valid_order_ids
    )

    print(
        "\nPayment order IDs missing "
        "from fact_orders:"
    )

    print(
        len(missing_order_ids)
    )

    if missing_order_ids:
        raise ValueError(
            "Some payment records do not "
            "match fact_orders."
        )

    # -----------------------------------------------------
    # 10. PAYMENT TYPE SUMMARY
    # -----------------------------------------------------

    print(
        "\nPayment type distribution:"
    )

    print(
        fact_payments[
            "payment_type"
        ]
        .value_counts()
    )

    # -----------------------------------------------------
    # 11. PAYMENT VALUE SUMMARY
    # -----------------------------------------------------

    total_payment_value = (
        fact_payments[
            "payment_value"
        ].sum()
    )

    print(
        "\nTotal payment value:"
    )

    print(
        f"{total_payment_value:,.2f}"
    )

    average_payment_value = (
        fact_payments[
            "payment_value"
        ].mean()
    )

    print(
        "\nAverage payment record value:"
    )

    print(
        f"{average_payment_value:,.2f}"
    )

    # -----------------------------------------------------
    # 12. INSTALLMENT SUMMARY
    # -----------------------------------------------------

    installment_payment_rows = (
        fact_payments[
            "is_installment_payment"
        ].sum()
    )

    print(
        "\nPayment records using "
        "multiple installments:"
    )

    print(
        f"{installment_payment_rows:,}"
    )

    # -----------------------------------------------------
    # 13. SAVE PROCESSED FACT TABLE
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    fact_payments.to_csv(
        FACT_PAYMENTS_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved fact_payments to:"
    )

    print(
        FACT_PAYMENTS_OUTPUT_FILE
    )

    print(
        "\nFACT_PAYMENTS BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_fact_payments()