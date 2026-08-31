from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROCESSED_DATA_PATH = Path("data/processed")

FACT_ORDERS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_orders.csv"
)

DIM_CUSTOMER_FILE = (
    PROCESSED_DATA_PATH
    / "dim_customer.csv"
)


# ---------------------------------------------------------
# VALIDATE CUSTOMER → ORDERS RELATIONSHIP
# ---------------------------------------------------------

def validate_customer_orders():
    """
    Validate the relationship between dim_customer
    and fact_orders using customer_id.
    """

    print("=" * 80)
    print("VALIDATING DIM_CUSTOMER → FACT_ORDERS")
    print("=" * 80)

    fact_orders = pd.read_csv(
        FACT_ORDERS_FILE
    )

    dim_customer = pd.read_csv(
        DIM_CUSTOMER_FILE
    )

    # -----------------------------------------------------
    # 1. CHECK DIMENSION KEY UNIQUENESS
    # -----------------------------------------------------

    duplicate_customer_ids = (
        dim_customer[
            "customer_id"
        ]
        .duplicated()
        .sum()
    )

    print(
        "\nDuplicate customer IDs "
        "in dim_customer:"
    )

    print(
        duplicate_customer_ids
    )

    if duplicate_customer_ids != 0:
        raise ValueError(
            "dim_customer.customer_id "
            "is not unique."
        )

    # -----------------------------------------------------
    # 2. FIND CUSTOMER IDs USED BY ORDERS
    #    THAT DO NOT EXIST IN DIM_CUSTOMER
    # -----------------------------------------------------

    fact_customer_ids = set(
        fact_orders[
            "customer_id"
        ].dropna()
    )

    dimension_customer_ids = set(
        dim_customer[
            "customer_id"
        ].dropna()
    )

    orphan_customer_ids = (
        fact_customer_ids
        - dimension_customer_ids
    )

    print(
        "\nCustomer IDs in fact_orders "
        "missing from dim_customer:"
    )

    print(
        len(orphan_customer_ids)
    )

    if orphan_customer_ids:
        raise ValueError(
            "Referential integrity failed: "
            "some fact_orders customer IDs "
            "do not exist in dim_customer."
        )

    # -----------------------------------------------------
    # 3. TEST THE JOIN
    # -----------------------------------------------------

    joined = fact_orders.merge(
        dim_customer,
        on="customer_id",
        how="left",
        validate="many_to_one"
    )

    print(
        "\nRows before join:"
    )

    print(
        f"{len(fact_orders):,}"
    )

    print(
        "Rows after join:"
    )

    print(
        f"{len(joined):,}"
    )

    if len(joined) != len(fact_orders):
        raise ValueError(
            "Join unexpectedly changed "
            "the fact_orders row count."
        )

    # -----------------------------------------------------
    # 4. CHECK CUSTOMER ATTRIBUTES AFTER JOIN
    # -----------------------------------------------------

    missing_unique_customers = (
        joined[
            "customer_unique_id"
        ]
        .isna()
        .sum()
    )

    print(
        "\nOrders missing "
        "customer_unique_id after join:"
    )

    print(
        missing_unique_customers
    )

    if missing_unique_customers != 0:
        raise ValueError(
            "Some orders failed to match "
            "a customer record."
        )

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    print(
        "\nRELATIONSHIP VALIDATION PASSED"
    )

    print(
        "dim_customer (1) "
        "→ fact_orders (many)"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    validate_customer_orders()