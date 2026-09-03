# Power BI Data Model Mapping

## Enterprise Retail Analytics & Operations Control Tower

This document defines how the dashboard-ready datasets should be
used inside Power BI.

---

# Modeling Strategy

The Power BI export layer contains pre-aggregated analytical datasets
created from validated SQL queries.

Each dataset has a different reporting grain.

Because of this, the exported analytical tables should NOT be joined
directly to each other simply because they contain similarly named
columns.

Doing so could create:

- many-to-many relationships
- duplicated revenue
- duplicated orders
- incorrect averages
- incorrect customer counts
- ambiguous filter paths

The safest design for the current dashboard is to treat the analytical
exports as independent reporting tables.

---

# Dataset Inventory

## 1. executive_kpis.csv

### Grain

One row = entire business

### Used For

Page 1 — Executive Overview

### Important Fields

- total_orders
- delivered_orders
- unique_customers
- active_sellers
- merchandise_value
- freight_value
- item_value_including_freight
- total_payment_value
- average_order_value
- average_delivery_time_days
- late_delivery_rate_pct
- average_review_score
- positive_review_rate_pct
- negative_review_rate_pct

### Relationship Guidance

Do not create relationships from this table.

This is a single-row executive summary table.

---

# 2. monthly_performance.csv

### Grain

One row = one purchase month

### Used For

Page 1 — Executive Overview

Page 3 — Delivery & Operations

### Important Fields

- year
- month
- month_name
- year_month
- year_month_sort
- total_orders
- delivered_orders
- merchandise_value
- freight_value
- payment_value
- average_order_value
- average_delivery_time_days
- late_delivery_rate_pct
- average_review_score
- positive_review_rate_pct
- negative_review_rate_pct

### Relationship Guidance

Keep independent.

Use year_month or year_month_sort for chart ordering.

---

# 3. product_performance.csv

### Grain

One row = one product category

### Used For

Page 2 — Sales & Product Performance

### Important Fields

- product_category
- orders
- items_sold
- merchandise_value
- freight_value
- item_value_including_freight
- average_item_price
- freight_share_pct
- average_delivery_time_days
- late_delivery_rate_pct
- average_review_score
- positive_review_rate_pct
- negative_review_rate_pct

### Relationship Guidance

Keep independent.

Do not connect directly to seller_performance or operational_risk.

---

# 4. seller_performance.csv

### Grain

One row = one seller

### Used For

Page 2 — Sales & Product Performance

Page 5 — Geographic & Risk Control Tower

### Important Fields

- seller_id
- seller_city
- seller_state
- revenue_rank
- order_volume_rank
- unique_products_sold
- orders
- unique_customers
- items_sold
- merchandise_value
- freight_value
- average_seller_order_value
- late_delivery_rate_pct
- average_review_score
- positive_review_rate_pct
- negative_review_rate_pct

### Relationship Guidance

Keep independent.

Seller-level metrics were already calculated at the correct grain
inside SQL.

---

# 5. geographic_performance.csv

### Grain

One row = one customer state

### Used For

Page 5 — Geographic & Risk Control Tower

### Important Fields

- customer_state
- revenue_rank
- order_volume_rank
- late_delivery_risk_rank
- orders
- unique_customers
- items_sold
- merchandise_value
- freight_value
- payment_value
- average_order_value
- average_delivery_time_days
- late_delivery_rate_pct
- average_review_score
- positive_review_rate_pct
- negative_review_rate_pct
- geography_coverage_pct
- average_customer_latitude
- average_customer_longitude

### Relationship Guidance

Keep independent.

This table is already aggregated to customer-state grain.

---

# 6. customer_behavior.csv

### Grain

One row = one unique customer

### Used For

Page 4 — Customer & Payment Behavior

### Important Fields

- customer_unique_id
- customer_value_rank
- customer_type
- order_frequency_segment
- lifetime_orders
- first_order_timestamp
- latest_order_timestamp
- customer_lifetime_days
- lifetime_items_purchased
- lifetime_merchandise_value
- lifetime_freight_value
- lifetime_payment_value
- average_order_value
- delivered_orders
- average_delivery_time_days
- late_delivery_rate_pct
- average_review_score

### Relationship Guidance

Keep independent.

This table is already aggregated to underlying-customer grain.

---

# 7. customer_segment_summary.csv

### Grain

One row = one customer type + frequency segment

### Used For

Page 4 — Customer & Payment Behavior

### Important Fields

- customer_type
- order_frequency_segment
- customers
- total_orders
- total_payment_value
- average_customer_value
- average_order_value
- average_review_score
- average_delivery_time_days

### Relationship Guidance

Keep independent.

Do not connect it to customer_behavior.

The same information originates from customer_behavior, but this table
was intentionally pre-aggregated for dashboard visuals.

---

# 8. payment_behavior.csv

### Grain

One row = one payment type

### Used For

Page 4 — Customer & Payment Behavior

### Important Fields

- payment_type
- orders_using_payment_type
- payment_records
- total_payment_value
- payment_record_share_pct
- payment_value_share_pct
- average_payment_value_per_order
- average_payment_record_value
- average_installments
- maximum_installments
- multi_installment_records
- multi_installment_record_rate_pct
- multi_method_orders
- multi_method_order_rate_pct

### Relationship Guidance

Keep independent.

One order can use more than one payment method.

Do not attempt to create relationships using order counts.

---

# 9. delivery_operations.csv

### Grain

One row = one delivery status

### Used For

Page 3 — Delivery & Operations

### Important Fields

- delivery_status
- orders
- order_share_pct
- reviewed_orders
- average_delivery_time_days
- average_delivery_delay_days
- average_review_score
- positive_review_rate_pct
- negative_review_rate_pct

### Relationship Guidance

Keep independent.

This is an aggregated operational summary.

---

# 10. operational_risk.csv

### Grain

One row = one operational entity

Entity types include:

- Seller
- Product Category
- Customer State

### Used For

Page 5 — Geographic & Risk Control Tower

### Important Fields

- entity_type
- entity_name
- management_priority
- operational_risk_score
- orders
- delivered_orders
- reviewed_orders
- merchandise_value
- average_delivery_time_days
- late_delivery_rate_pct
- overall_late_delivery_rate_pct
- late_delivery_gap_pp
- average_review_score
- overall_average_review_score
- review_score_gap
- negative_review_rate_pct
- overall_negative_review_rate_pct
- negative_review_gap_pp
- revenue_percentile_pct
- order_volume_percentile_pct

### Relationship Guidance

Keep independent.

Do NOT link:

entity_name

to:

- seller_id
- product_category
- customer_state

because entity_name contains values from three different entity types.

---

# Recommended Power BI Model

The analytical export model should appear approximately like this:

executive_kpis

monthly_performance

product_performance

seller_performance

geographic_performance

customer_behavior

customer_segment_summary

payment_behavior

delivery_operations

operational_risk

There should be NO relationships between these analytical export
tables in the initial dashboard model.

---

# Why No Relationships?

The SQL layer has already solved:

- source grain
- duplicate prevention
- fact aggregation
- dimensional enrichment
- financial reconciliation
- customer identity resolution
- operational segmentation

Power BI is being used primarily as the visualization and
decision-support layer.

Rebuilding those relationships inside Power BI could reintroduce
grain problems already solved in SQL.

---

# Page-to-Dataset Mapping

## Page 1 — Executive Overview

Use:

- executive_kpis
- monthly_performance
- delivery_operations

---

## Page 2 — Sales & Product Performance

Use:

- product_performance
- seller_performance

---

## Page 3 — Delivery & Operations

Use:

- delivery_operations
- monthly_performance

---

## Page 4 — Customer & Payment Behavior

Use:

- customer_behavior
- customer_segment_summary
- payment_behavior

---

## Page 5 — Geographic & Risk Control Tower

Use:

- geographic_performance
- operational_risk
- seller_performance

---

# Filter Strategy

Because the current analytical tables are disconnected,
filters should initially be page-specific.

Examples:

Product page:

- Product Category

Seller analysis:

- Seller State

Geography page:

- Customer State

Risk page:

- Entity Type
- Management Priority

Customer page:

- Customer Type
- Order Frequency Segment

Payment section:

- Payment Type

---

# Important Limitation

A slicer from one disconnected analytical table will not automatically
filter visuals built from another analytical table.

For example:

A customer-state slicer from geographic_performance will not filter
product_performance.

This is intentional in the initial analytical model.

If fully synchronized cross-page filtering is required later, the
dashboard should move to a true Power BI star schema using the
processed fact and dimension tables rather than joining the
pre-aggregated analytical exports.

---

# Data Modeling Principle

Perform complex grain management and reconciliation upstream.

Use Power BI for:

- visualization
- interaction
- KPI communication
- business storytelling
- exception identification

Avoid recreating already validated transformations in the reporting
layer.