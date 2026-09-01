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

FACT_ORDER_ITEMS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_order_items.csv"
)

FACT_REVIEWS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_reviews.csv"
)

DIM_DATE_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "dim_date.csv"
)


# ---------------------------------------------------------
# BUILD DIM DATE
# ---------------------------------------------------------

def build_dim_date():
    """
    Build a continuous calendar dimension covering
    all relevant dates in the analytical model.

    Grain:
    One row = one calendar date.
    """

    print("=" * 80)
    print("BUILDING DIM_DATE")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. LOAD ANALYTICAL TABLES
    # -----------------------------------------------------

    orders = pd.read_csv(
        FACT_ORDERS_FILE
    )

    order_items = pd.read_csv(
        FACT_ORDER_ITEMS_FILE
    )

    reviews = pd.read_csv(
        FACT_REVIEWS_FILE
    )

    # -----------------------------------------------------
    # 2. DEFINE DATE/TIMESTAMP COLUMNS
    # -----------------------------------------------------

    order_date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    order_item_date_columns = [
        "shipping_limit_date",
    ]

    review_date_columns = [
        "review_creation_date",
        "review_answer_timestamp",
    ]

    # -----------------------------------------------------
    # 3. CONVERT COLUMNS TO DATETIME
    # -----------------------------------------------------

    for column in order_date_columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )

    for column in order_item_date_columns:
        order_items[column] = pd.to_datetime(
            order_items[column],
            errors="coerce"
        )

    for column in review_date_columns:
        reviews[column] = pd.to_datetime(
            reviews[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # 4. COLLECT ALL DATE VALUES
    # -----------------------------------------------------

    all_date_series = []

    for column in order_date_columns:
        all_date_series.append(
            orders[column]
        )

    for column in order_item_date_columns:
        all_date_series.append(
            order_items[column]
        )

    for column in review_date_columns:
        all_date_series.append(
            reviews[column]
        )

    all_dates = pd.concat(
        all_date_series,
        ignore_index=True
    ).dropna()

    # -----------------------------------------------------
    # 5. DETERMINE CALENDAR RANGE
    # -----------------------------------------------------

    min_date = (
        all_dates
        .min()
        .normalize()
    )

    max_date = (
        all_dates
        .max()
        .normalize()
    )

    print(
        "\nCalendar start date:"
    )

    print(
        min_date.date()
    )

    print(
        "\nCalendar end date:"
    )

    print(
        max_date.date()
    )

    # -----------------------------------------------------
    # 6. GENERATE CONTINUOUS DATE RANGE
    # -----------------------------------------------------

    calendar_dates = pd.date_range(
        start=min_date,
        end=max_date,
        freq="D"
    )

    dim_date = pd.DataFrame(
        {
            "date": calendar_dates
        }
    )

    print(
        "\nCalendar rows generated:"
    )

    print(
        f"{len(dim_date):,}"
    )

    # -----------------------------------------------------
    # 7. CREATE DATE KEY
    # -----------------------------------------------------

    dim_date[
        "date_key"
    ] = (
        dim_date[
            "date"
        ]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    # -----------------------------------------------------
    # 8. YEAR ATTRIBUTES
    # -----------------------------------------------------

    dim_date[
        "year"
    ] = (
        dim_date[
            "date"
        ].dt.year
    )

    dim_date[
        "quarter_number"
    ] = (
        dim_date[
            "date"
        ].dt.quarter
    )

    dim_date[
        "quarter"
    ] = (
        "Q"
        +
        dim_date[
            "quarter_number"
        ].astype(str)
    )

    dim_date[
        "year_quarter"
    ] = (
        dim_date[
            "year"
        ].astype(str)
        +
        "-"
        +
        dim_date[
            "quarter"
        ]
    )

    # -----------------------------------------------------
    # 9. MONTH ATTRIBUTES
    # -----------------------------------------------------

    dim_date[
        "month_number"
    ] = (
        dim_date[
            "date"
        ].dt.month
    )

    dim_date[
        "month_name"
    ] = (
        dim_date[
            "date"
        ].dt.month_name()
    )

    dim_date[
        "month_short"
    ] = (
        dim_date[
            "date"
        ]
        .dt.strftime("%b")
    )

    dim_date[
        "year_month"
    ] = (
        dim_date[
            "date"
        ]
        .dt.strftime("%Y-%m")
    )

    dim_date[
        "year_month_sort"
    ] = (
        dim_date[
            "year"
        ] * 100
        +
        dim_date[
            "month_number"
        ]
    )

    # -----------------------------------------------------
    # 10. WEEK ATTRIBUTES
    # -----------------------------------------------------

    dim_date[
        "week_of_year"
    ] = (
        dim_date[
            "date"
        ]
        .dt
        .isocalendar()
        .week
        .astype(int)
    )

    # -----------------------------------------------------
    # 11. DAY ATTRIBUTES
    # -----------------------------------------------------

    dim_date[
        "day_of_month"
    ] = (
        dim_date[
            "date"
        ].dt.day
    )

    dim_date[
        "day_of_week_number"
    ] = (
        dim_date[
            "date"
        ].dt.dayofweek
        + 1
    )

    dim_date[
        "day_name"
    ] = (
        dim_date[
            "date"
        ].dt.day_name()
    )

    dim_date[
        "day_short"
    ] = (
        dim_date[
            "date"
        ]
        .dt.strftime("%a")
    )

    # -----------------------------------------------------
    # 12. WEEKEND FLAG
    # -----------------------------------------------------

    dim_date[
        "is_weekend"
    ] = (
        dim_date[
            "day_of_week_number"
        ].isin(
            [6, 7]
        )
        .astype(int)
    )

    # -----------------------------------------------------
    # 13. MONTH START / END FLAGS
    # -----------------------------------------------------

    dim_date[
        "is_month_start"
    ] = (
        dim_date[
            "date"
        ]
        .dt
        .is_month_start
        .astype(int)
    )

    dim_date[
        "is_month_end"
    ] = (
        dim_date[
            "date"
        ]
        .dt
        .is_month_end
        .astype(int)
    )

    # -----------------------------------------------------
    # 14. VALIDATE DIMENSION GRAIN
    # -----------------------------------------------------

    duplicate_dates = (
        dim_date[
            "date"
        ]
        .duplicated()
        .sum()
    )

    duplicate_date_keys = (
        dim_date[
            "date_key"
        ]
        .duplicated()
        .sum()
    )

    print(
        "\nDuplicate dates:"
    )

    print(
        duplicate_dates
    )

    print(
        "\nDuplicate date keys:"
    )

    print(
        duplicate_date_keys
    )

    if duplicate_dates != 0:
        raise ValueError(
            "dim_date contains duplicate dates."
        )

    if duplicate_date_keys != 0:
        raise ValueError(
            "dim_date contains duplicate date keys."
        )

    # -----------------------------------------------------
    # 15. VALIDATE CONTINUOUS CALENDAR
    # -----------------------------------------------------

    expected_rows = (
        max_date
        - min_date
    ).days + 1

    print(
        "\nExpected calendar rows:"
    )

    print(
        f"{expected_rows:,}"
    )

    print(
        "\nActual calendar rows:"
    )

    print(
        f"{len(dim_date):,}"
    )

    if (
        len(dim_date)
        != expected_rows
    ):
        raise ValueError(
            "dim_date does not contain "
            "a continuous calendar."
        )

    # -----------------------------------------------------
    # 16. SELECT FINAL COLUMN ORDER
    # -----------------------------------------------------

    dim_date = dim_date[
        [
            "date_key",
            "date",
            "year",
            "quarter_number",
            "quarter",
            "year_quarter",
            "month_number",
            "month_name",
            "month_short",
            "year_month",
            "year_month_sort",
            "week_of_year",
            "day_of_month",
            "day_of_week_number",
            "day_name",
            "day_short",
            "is_weekend",
            "is_month_start",
            "is_month_end",
        ]
    ]

    # -----------------------------------------------------
    # 17. SAVE DATE DIMENSION
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    dim_date.to_csv(
        DIM_DATE_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved dim_date to:"
    )

    print(
        DIM_DATE_OUTPUT_FILE
    )

    print(
        "\nDIM_DATE BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_dim_date()