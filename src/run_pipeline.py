import time

from build_fact_orders import build_fact_orders
from build_dim_customer import build_dim_customer
from build_dim_product import build_dim_product
from build_dim_seller import build_dim_seller
from build_fact_order_items import build_fact_order_items
from build_fact_payments import build_fact_payments
from build_fact_reviews import build_fact_reviews
from build_dim_date import build_dim_date
from build_dim_geography import build_dim_geography

from validate_model_relationships import (
    validate_customer_orders,
)

from reconcile_order_financials import (
    reconcile_order_financials,
)

from analyze_delivery_satisfaction import (
    analyze_delivery_satisfaction,
)


# ---------------------------------------------------------
# PIPELINE HELPER
# ---------------------------------------------------------

def run_step(step_number, step_name, function):
    """
    Run one pipeline step and report its execution time.
    """

    print("\n" + "=" * 80)
    print(
        f"STEP {step_number}: "
        f"{step_name}"
    )
    print("=" * 80)

    start_time = time.time()

    try:
        function()

    except Exception as error:
        print("\n" + "!" * 80)
        print(
            f"PIPELINE FAILED DURING: "
            f"{step_name}"
        )
        print("!" * 80)

        print(
            f"\nError type: "
            f"{type(error).__name__}"
        )

        print(
            f"Error message: "
            f"{error}"
        )

        raise

    end_time = time.time()

    elapsed_seconds = (
        end_time
        -
        start_time
    )

    print(
        f"\nSTEP COMPLETED IN "
        f"{elapsed_seconds:.2f} SECONDS"
    )


# ---------------------------------------------------------
# MASTER ANALYTICS PIPELINE
# ---------------------------------------------------------

def run_pipeline():
    """
    Build, validate, and analyze the complete
    retail analytical model.
    """

    pipeline_start = time.time()

    print("\n" + "=" * 80)
    print(
        "ENTERPRISE RETAIL ANALYTICS "
        "& OPERATIONS CONTROL TOWER"
    )
    print("MASTER DATA PIPELINE")
    print("=" * 80)

    # -----------------------------------------------------
    # CORE MODEL BUILD
    # -----------------------------------------------------

    run_step(
        1,
        "Build fact_orders",
        build_fact_orders,
    )

    run_step(
        2,
        "Build dim_customer",
        build_dim_customer,
    )

    run_step(
        3,
        "Build dim_product",
        build_dim_product,
    )

    run_step(
        4,
        "Build dim_seller",
        build_dim_seller,
    )

    run_step(
        5,
        "Build fact_order_items",
        build_fact_order_items,
    )

    run_step(
        6,
        "Build fact_payments",
        build_fact_payments,
    )

    run_step(
        7,
        "Build fact_reviews",
        build_fact_reviews,
    )

    run_step(
        8,
        "Build dim_date",
        build_dim_date,
    )

    run_step(
        9,
        "Build dim_geography",
        build_dim_geography,
    )

    # -----------------------------------------------------
    # MODEL VALIDATION
    # -----------------------------------------------------

    run_step(
        10,
        "Validate model relationships",
        validate_customer_orders,
    )

    # -----------------------------------------------------
    # CROSS-FACT RECONCILIATION
    # -----------------------------------------------------

    run_step(
        11,
        "Reconcile order financials",
        reconcile_order_financials,
    )

    # -----------------------------------------------------
    # BUSINESS ANALYSIS
    # -----------------------------------------------------

    run_step(
        12,
        "Analyze delivery satisfaction",
        analyze_delivery_satisfaction,
    )

    # -----------------------------------------------------
    # PIPELINE COMPLETE
    # -----------------------------------------------------

    pipeline_end = time.time()

    total_seconds = (
        pipeline_end
        -
        pipeline_start
    )

    total_minutes = (
        total_seconds
        / 60
    )

    print("\n" + "=" * 80)
    print("MASTER PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)

    print(
        "\nAnalytical tables created:"
    )

    print(
        """
DIMENSIONS
  - dim_customer
  - dim_product
  - dim_seller
  - dim_date
  - dim_geography

FACTS
  - fact_orders
  - fact_order_items
  - fact_payments
  - fact_reviews

ANALYTICAL OUTPUTS
  - delivery_satisfaction_summary
"""
    )

    print(
        "Validation completed:"
    )

    print(
        """
  - Source grain validation
  - Primary/composite key validation
  - Referential integrity validation
  - Financial reconciliation
  - Delivery/customer satisfaction analysis
"""
    )

    print(
        f"Total pipeline runtime: "
        f"{total_seconds:.2f} seconds"
    )

    print(
        f"Total pipeline runtime: "
        f"{total_minutes:.2f} minutes"
    )

    print(
        "\nPIPELINE STATUS: SUCCESS"
    )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    run_pipeline()