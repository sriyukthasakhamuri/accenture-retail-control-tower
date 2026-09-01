from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = Path("data/raw")
PROCESSED_DATA_PATH = Path("data/processed")

REVIEWS_SOURCE_FILE = (
    RAW_DATA_PATH
    / "olist_order_reviews_dataset.csv"
)

FACT_REVIEWS_OUTPUT_FILE = (
    PROCESSED_DATA_PATH
    / "fact_reviews.csv"
)

FACT_ORDERS_FILE = (
    PROCESSED_DATA_PATH
    / "fact_orders.csv"
)


# ---------------------------------------------------------
# BUILD FACT REVIEWS
# ---------------------------------------------------------

def build_fact_reviews():
    """
    Build an analytics-ready review fact table.

    Grain:
    One row = one review record associated
    with an order.

    Candidate key:
    review_id + order_id
    """

    print("=" * 80)
    print("BUILDING FACT_REVIEWS")
    print("=" * 80)

    # -----------------------------------------------------
    # 1. READ RAW REVIEW DATA
    # -----------------------------------------------------

    reviews_df = pd.read_csv(
        REVIEWS_SOURCE_FILE
    )

    print(
        f"\nRaw review rows: "
        f"{len(reviews_df):,}"
    )

    # -----------------------------------------------------
    # 2. VALIDATE COMPOSITE KEY
    # -----------------------------------------------------

    unique_review_keys = (
        reviews_df[
            [
                "review_id",
                "order_id",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        "Unique review_id + order_id "
        f"combinations: {unique_review_keys:,}"
    )

    if (
        len(reviews_df)
        != unique_review_keys
    ):
        raise ValueError(
            "Review source does not have a "
            "unique review_id + order_id grain."
        )

    # -----------------------------------------------------
    # 3. CONVERT REVIEW TIMESTAMPS
    # -----------------------------------------------------

    timestamp_columns = [
        "review_creation_date",
        "review_answer_timestamp",
    ]

    for column in timestamp_columns:
        reviews_df[column] = pd.to_datetime(
            reviews_df[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # 4. CHECK REVIEW SCORE QUALITY
    # -----------------------------------------------------

    print(
        "\nReview score distribution:"
    )

    print(
        reviews_df[
            "review_score"
        ]
        .value_counts()
        .sort_index()
    )

    invalid_review_scores = (
        ~reviews_df[
            "review_score"
        ].between(1, 5)
    ).sum()

    print(
        "\nReview scores outside 1-5:"
    )

    print(
        invalid_review_scores
    )

    if invalid_review_scores != 0:
        raise ValueError(
            "Invalid review scores detected."
        )

    # -----------------------------------------------------
    # 5. CHECK MISSING REVIEW CONTENT
    # -----------------------------------------------------

    print(
        "\nMissing review fields:"
    )

    print(
        reviews_df[
            [
                "review_comment_title",
                "review_comment_message",
                "review_creation_date",
                "review_answer_timestamp",
            ]
        ]
        .isna()
        .sum()
    )

    # -----------------------------------------------------
    # 6. CREATE COMMENT FLAGS
    # -----------------------------------------------------

    reviews_df[
        "has_comment_title"
    ] = (
        reviews_df[
            "review_comment_title"
        ]
        .notna()
        .astype(int)
    )

    reviews_df[
        "has_comment_message"
    ] = (
        reviews_df[
            "review_comment_message"
        ]
        .notna()
        .astype(int)
    )

    # -----------------------------------------------------
    # 7. CREATE SATISFACTION FLAGS
    # -----------------------------------------------------

    reviews_df[
        "is_positive_review"
    ] = (
        reviews_df[
            "review_score"
        ] >= 4
    ).astype(int)

    reviews_df[
        "is_negative_review"
    ] = (
        reviews_df[
            "review_score"
        ] <= 2
    ).astype(int)

    reviews_df[
        "is_neutral_review"
    ] = (
        reviews_df[
            "review_score"
        ] == 3
    ).astype(int)

    # -----------------------------------------------------
    # 8. CALCULATE REVIEW RESPONSE TIME
    # -----------------------------------------------------

    reviews_df[
        "review_response_time_hours"
    ] = (
        (
            reviews_df[
                "review_answer_timestamp"
            ]
            -
            reviews_df[
                "review_creation_date"
            ]
        )
        .dt.total_seconds()
        / 3600
    )

    # -----------------------------------------------------
    # 9. SELECT FACT TABLE COLUMNS
    # -----------------------------------------------------

    fact_reviews = reviews_df[
        [
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
            "review_response_time_hours",
            "has_comment_title",
            "has_comment_message",
            "is_positive_review",
            "is_negative_review",
            "is_neutral_review",
        ]
    ].copy()

    # -----------------------------------------------------
    # 10. VALIDATE OUTPUT GRAIN
    # -----------------------------------------------------

    output_rows = len(
        fact_reviews
    )

    output_unique_keys = (
        fact_reviews[
            [
                "review_id",
                "order_id",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        f"\nProcessed review rows: "
        f"{output_rows:,}"
    )

    print(
        "Processed unique review keys: "
        f"{output_unique_keys:,}"
    )

    if (
        output_rows
        != len(reviews_df)
    ):
        raise ValueError(
            "fact_reviews row count "
            "changed during transformation."
        )

    if (
        output_rows
        != output_unique_keys
    ):
        raise ValueError(
            "fact_reviews grain "
            "validation failed."
        )

    # -----------------------------------------------------
    # 11. VALIDATE RELATIONSHIP TO FACT_ORDERS
    # -----------------------------------------------------

    fact_orders = pd.read_csv(
        FACT_ORDERS_FILE
    )

    review_order_ids = set(
        fact_reviews[
            "order_id"
        ].dropna()
    )

    valid_order_ids = set(
        fact_orders[
            "order_id"
        ].dropna()
    )

    missing_order_ids = (
        review_order_ids
        -
        valid_order_ids
    )

    print(
        "\nReview order IDs missing "
        "from fact_orders:"
    )

    print(
        len(missing_order_ids)
    )

    if missing_order_ids:
        raise ValueError(
            "Some review records do not "
            "match fact_orders."
        )

    # -----------------------------------------------------
    # 12. REVIEW KPI SUMMARY
    # -----------------------------------------------------

    average_review_score = (
        fact_reviews[
            "review_score"
        ].mean()
    )

    positive_reviews = (
        fact_reviews[
            "is_positive_review"
        ].sum()
    )

    negative_reviews = (
        fact_reviews[
            "is_negative_review"
        ].sum()
    )

    neutral_reviews = (
        fact_reviews[
            "is_neutral_review"
        ].sum()
    )

    print(
        "\nAverage review score:"
    )

    print(
        f"{average_review_score:.2f}"
    )

    print(
        "\nPositive reviews (4-5):"
    )

    print(
        f"{positive_reviews:,}"
    )

    print(
        "\nNeutral reviews (3):"
    )

    print(
        f"{neutral_reviews:,}"
    )

    print(
        "\nNegative reviews (1-2):"
    )

    print(
        f"{negative_reviews:,}"
    )

    # -----------------------------------------------------
    # 13. SAVE PROCESSED FACT TABLE
    # -----------------------------------------------------

    PROCESSED_DATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    fact_reviews.to_csv(
        FACT_REVIEWS_OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved fact_reviews to:"
    )

    print(
        FACT_REVIEWS_OUTPUT_FILE
    )

    print(
        "\nFACT_REVIEWS BUILD COMPLETE"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    build_fact_reviews()