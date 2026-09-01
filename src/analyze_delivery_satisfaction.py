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

FACT_REVIEWS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_reviews.csv"
)

DELIVERY_SATISFACTION_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "delivery_satisfaction_summary.csv"
)


# ---------------------------------------------------------
# DELIVERY VS CUSTOMER SATISFACTION ANALYSIS
# ---------------------------------------------------------

def analyze_delivery_satisfaction():
    """
    Analyze whether delivery performance is associated
    with customer review scores.

    Both datasets are aligned to one row per order
    before comparison.
    """

    print("=" * 80)
    print("DELIVERY PERFORMANCE VS CUSTOMER SATISFACTION")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. LOAD ANALYTICAL TABLES
    # -----------------------------------------------------

    orders = pd.read_csv(
        FACT_ORDERS_FILE
    )

    reviews = pd.read_csv(
        FACT_REVIEWS_FILE
    )

    print(
        f"\nOrders loaded: "
        f"{len(orders):,}"
    )

    print(
        f"Review records loaded: "
        f"{len(reviews):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE ORDERS GRAIN
    # -----------------------------------------------------

    duplicate_order_ids = (
        orders[
            "order_id"
        ]
        .duplicated()
        .sum()
    )

    print(
        "\nDuplicate order IDs in fact_orders:"
    )

    print(
        duplicate_order_ids
    )

    if duplicate_order_ids != 0:
        raise ValueError(
            "fact_orders is not one row per order."
        )

    # -----------------------------------------------------
    # 3. CHECK REVIEW COVERAGE
    # -----------------------------------------------------

    reviewed_orders = (
        reviews[
            "order_id"
        ].nunique()
    )

    print(
        "\nUnique orders with reviews:"
    )

    print(
        f"{reviewed_orders:,}"
    )

    reviews_per_order = (
        reviews
        .groupby(
            "order_id"
        )
        .size()
    )

    orders_with_multiple_reviews = (
        reviews_per_order > 1
    ).sum()

    print(
        "\nOrders with multiple "
        "review records:"
    )

    print(
        f"{orders_with_multiple_reviews:,}"
    )

    # -----------------------------------------------------
    # 4. AGGREGATE REVIEWS TO ORDER GRAIN
    # -----------------------------------------------------

    review_by_order = (
        reviews
        .groupby(
            "order_id",
            as_index=False
        )
        .agg(
            review_record_count=(
                "review_id",
                "count"
            ),
            average_review_score=(
                "review_score",
                "mean"
            ),
            positive_review_records=(
                "is_positive_review",
                "sum"
            ),
            neutral_review_records=(
                "is_neutral_review",
                "sum"
            ),
            negative_review_records=(
                "is_negative_review",
                "sum"
            ),
        )
    )

    print(
        "\nReview rows after aggregation "
        "to order grain:"
    )

    print(
        f"{len(review_by_order):,}"
    )

    # -----------------------------------------------------
    # 5. CREATE ORDER-LEVEL SATISFACTION FLAGS
    # -----------------------------------------------------

    review_by_order[
        "is_positive_order_review"
    ] = (
        review_by_order[
            "average_review_score"
        ] >= 4
    ).astype(int)

    review_by_order[
        "is_negative_order_review"
    ] = (
        review_by_order[
            "average_review_score"
        ] <= 2
    ).astype(int)

    review_by_order[
        "is_neutral_order_review"
    ] = (
        (
            review_by_order[
                "average_review_score"
            ] > 2
        )
        &
        (
            review_by_order[
                "average_review_score"
            ] < 4
        )
    ).astype(int)

    # -----------------------------------------------------
    # 6. JOIN ORDERS TO ORDER-LEVEL REVIEWS
    # -----------------------------------------------------

    analysis = orders.merge(
        review_by_order,
        on="order_id",
        how="inner",
        validate="one_to_one"
    )

    print(
        "\nOrders with both delivery "
        "and review information:"
    )

    print(
        f"{len(analysis):,}"
    )

    # -----------------------------------------------------
    # 7. KEEP DELIVERED ORDERS WITH VALID DELIVERY DATA
    # -----------------------------------------------------

    delivered_analysis = (
        analysis[
            (
                analysis[
                    "is_delivered"
                ] == 1
            )
            &
            (
                analysis[
                    "delivery_delay_days"
                ].notna()
            )
        ]
        .copy()
    )

    print(
        "\nDelivered reviewed orders "
        "with valid delivery dates:"
    )

    print(
        f"{len(delivered_analysis):,}"
    )

    # -----------------------------------------------------
    # 8. CLASSIFY DELIVERY PERFORMANCE
    # -----------------------------------------------------

    delivered_analysis[
        "delivery_performance"
    ] = "On Time / Early"

    delivered_analysis.loc[
        delivered_analysis[
            "delivery_delay_days"
        ] > 0,
        "delivery_performance"
    ] = "Late"

    print(
        "\nDelivery performance distribution:"
    )

    print(
        delivered_analysis[
            "delivery_performance"
        ]
        .value_counts()
    )

    # -----------------------------------------------------
    # 9. BUILD SATISFACTION SUMMARY
    # -----------------------------------------------------

    summary = (
        delivered_analysis
        .groupby(
            "delivery_performance",
            as_index=False
        )
        .agg(
            orders=(
                "order_id",
                "nunique"
            ),
            average_review_score=(
                "average_review_score",
                "mean"
            ),
            positive_review_rate=(
                "is_positive_order_review",
                "mean"
            ),
            negative_review_rate=(
                "is_negative_order_review",
                "mean"
            ),
            average_delivery_days=(
                "delivery_time_days",
                "mean"
            ),
            average_delay_days=(
                "delivery_delay_days",
                "mean"
            ),
        )
    )

    # Convert rates to percentages
    summary[
        "positive_review_rate"
    ] = (
        summary[
            "positive_review_rate"
        ] * 100
    )

    summary[
        "negative_review_rate"
    ] = (
        summary[
            "negative_review_rate"
        ] * 100
    )

    # Round reporting metrics
    summary[
        "average_review_score"
    ] = (
        summary[
            "average_review_score"
        ].round(2)
    )

    summary[
        "positive_review_rate"
    ] = (
        summary[
            "positive_review_rate"
        ].round(2)
    )

    summary[
        "negative_review_rate"
    ] = (
        summary[
            "negative_review_rate"
        ].round(2)
    )

    summary[
        "average_delivery_days"
    ] = (
        summary[
            "average_delivery_days"
        ].round(2)
    )

    summary[
        "average_delay_days"
    ] = (
        summary[
            "average_delay_days"
        ].round(2)
    )

    # -----------------------------------------------------
    # 10. DISPLAY SUMMARY
    # -----------------------------------------------------

    print(
        "\nDelivery satisfaction summary:"
    )

    print(
        summary.to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # 11. COMPARE LATE VS ON-TIME
    # -----------------------------------------------------

    late_row = summary[
        summary[
            "delivery_performance"
        ] == "Late"
    ]

    on_time_row = summary[
        summary[
            "delivery_performance"
        ] == "On Time / Early"
    ]

    if (
        not late_row.empty
        and not on_time_row.empty
    ):

        late_score = (
            late_row[
                "average_review_score"
            ].iloc[0]
        )

        on_time_score = (
            on_time_row[
                "average_review_score"
            ].iloc[0]
        )

        review_score_difference = (
            on_time_score
            -
            late_score
        )

        late_negative_rate = (
            late_row[
                "negative_review_rate"
            ].iloc[0]
        )

        on_time_negative_rate = (
            on_time_row[
                "negative_review_rate"
            ].iloc[0]
        )

        negative_rate_difference = (
            late_negative_rate
            -
            on_time_negative_rate
        )

        print(
            "\nAverage review score difference "
            "(On Time/Early - Late):"
        )

        print(
            f"{review_score_difference:.2f}"
        )

        print(
            "\nIncrease in negative review rate "
            "for late deliveries:"
        )

        print(
            f"{negative_rate_difference:.2f} "
            "percentage points"
        )

    # -----------------------------------------------------
    # 12. SAVE ANALYSIS SUMMARY
    # -----------------------------------------------------

    summary.to_csv(
        DELIVERY_SATISFACTION_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved analysis summary to:"
    )

    print(
        DELIVERY_SATISFACTION_OUTPUT_FILE
    )

    print(
        "\nDELIVERY SATISFACTION ANALYSIS COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    analyze_delivery_satisfaction()