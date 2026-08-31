# Analytical Data Model Design

## Purpose

This document defines the analytical data model for the Enterprise Retail
Analytics & Operations Control Tower.

The source-system assessment identified datasets with different grains,
including orders, order items, payments, reviews, customers, products,
sellers, and geographic reference data.

The analytical model separates measurable business events into fact tables
and descriptive business entities into dimensions in order to reduce
double-counting risk and support scalable reporting.

---

# Modeling Approach

The project will use a star-schema-oriented analytical design.

The primary design principles are:

- Preserve the grain of each fact table.
- Avoid joining multiple one-to-many datasets into a single uncontrolled table.
- Use dimensions for reusable descriptive attributes.
- Standardize business keys and relationships.
- Create KPI calculations at the appropriate business grain.
- Support Power BI using primarily one-to-many relationships.
- Keep raw source data separate from analytics-ready structures.

---

# Proposed Fact Tables

## 1. fact_order_items

### Grain

One row represents one item position within an order.

### Source

`olist_order_items_dataset.csv`

### Candidate Key

`order_id + order_item_id`

### Core Fields

- order_id
- order_item_id
- product_id
- seller_id
- shipping_limit_date
- price
- freight_value

### Analytical Purpose

This will be the primary sales transaction fact table.

It will support measures such as:

- Item sales amount
- Freight amount
- Number of items sold
- Product sales
- Seller sales
- Category sales

### Important Modeling Rule

Revenue based on item price should be calculated at the order-item grain.

Payment values should not be joined directly into this fact without
aggregation because orders may contain multiple order items and multiple
payment records.

---

## 2. fact_orders

### Grain

One row represents one order.

### Source

`olist_orders_dataset.csv`

### Candidate Key

`order_id`

### Core Fields

- order_id
- customer_id
- order_status
- order_purchase_timestamp
- order_approved_at
- order_delivered_carrier_date
- order_delivered_customer_date
- order_estimated_delivery_date

### Derived Measures / Attributes

Potential derived fields include:

- approval_time_hours
- carrier_handoff_time_hours
- delivery_time_days
- delivery_delay_days
- is_late_delivery
- is_canceled
- is_delivered

### Analytical Purpose

This fact will support operational and fulfillment KPIs such as:

- Total orders
- Delivered orders
- Cancellation rate
- Late-delivery rate
- Average delivery time
- Average fulfillment time

---

## 3. fact_payments

### Grain

One row represents one payment sequence associated with an order.

### Source

`olist_order_payments_dataset.csv`

### Candidate Key

`order_id + payment_sequential`

### Core Fields

- order_id
- payment_sequential
- payment_type
- payment_installments
- payment_value

### Analytical Purpose

This fact will support:

- Total payment value
- Payment method distribution
- Installment analysis
- Multiple-payment behavior

### Modeling Consideration

Payments operate at a different grain than order items.

Payment amounts should therefore be aggregated independently when creating
order-level or enterprise-level financial KPIs.

---

## 4. fact_reviews

### Grain

One row represents one review record associated with an order.

### Source

`olist_order_reviews_dataset.csv`

### Candidate Key

`review_id + order_id`

### Core Fields

- review_id
- order_id
- review_score
- review_comment_title
- review_comment_message
- review_creation_date
- review_answer_timestamp

### Analytical Purpose

This fact will support:

- Average review score
- Review-score distribution
- Customer-satisfaction analysis
- Relationship between delivery performance and review scores

---

# Proposed Dimension Tables

## 1. dim_customer

### Source

`olist_customers_dataset.csv`

### Business Key

`customer_id`

### Important Customer Identifier

`customer_unique_id`

### Core Attributes

- customer_id
- customer_unique_id
- customer_zip_code_prefix
- customer_city
- customer_state

### Analytical Purpose

The dimension will support:

- Customer geography
- Repeat-customer analysis
- Customer purchase frequency
- Customer-level segmentation

### Modeling Note

`customer_id` identifies an order-level customer record.

`customer_unique_id` should be used when analysis requires identifying the
same underlying customer across multiple orders.

---

## 2. dim_product

### Sources

- `olist_products_dataset.csv`
- `product_category_name_translation.csv`

### Business Key

`product_id`

### Core Attributes

- product_id
- product_category_name
- product_category_name_english
- product_name_length
- product_description_length
- product_photos_qty
- product_weight_g
- product_length_cm
- product_height_cm
- product_width_cm

### Analytical Purpose

The dimension will support:

- Product analysis
- Product-category analysis
- Product characteristics
- Category-level revenue reporting

### Modeling Note

The translation table will be merged into the product dimension so that
English category names are available directly for reporting.

---

## 3. dim_seller

### Source

`olist_sellers_dataset.csv`

### Business Key

`seller_id`

### Core Attributes

- seller_id
- seller_zip_code_prefix
- seller_city
- seller_state

### Analytical Purpose

The dimension will support:

- Seller performance
- Seller geography
- Seller revenue
- Seller delivery-performance comparisons

---

## 4. dim_date

### Source

Generated analytically from source timestamps.

### Grain

One row represents one calendar date.

### Core Attributes

- date
- year
- quarter
- month_number
- month_name
- year_month
- week_number
- day_of_week
- day_name

### Analytical Purpose

The Date dimension will allow consistent analysis by:

- Day
- Week
- Month
- Quarter
- Year

The primary reporting relationship will initially use the order purchase date.

Additional date relationships may later be required for approval,
shipment, delivery, and review dates.

---

## 5. dim_geography

### Source

`olist_geolocation_dataset.csv`

### Proposed Grain

One representative record per zip-code prefix.

### Core Attributes

- zip_code_prefix
- latitude
- longitude
- city
- state

### Source Data Issue

The raw geolocation table contains:

- 1,000,163 rows
- 19,015 unique zip-code prefixes
- 261,831 exact duplicate rows

Therefore the raw dataset cannot be used directly as a one-row-per-zip
dimension.

### Proposed Transformation

The geolocation data will be cleaned and aggregated to create one
representative geographic record per zip-code prefix.

A possible approach is to calculate representative latitude and longitude
values for each prefix while retaining standardized city and state
information.

---

# Proposed Relationships

The initial analytical model will contain the following relationships:

- `dim_customer.customer_id`
  → `fact_orders.customer_id`

- `fact_orders.order_id`
  → `fact_order_items.order_id`

- `fact_orders.order_id`
  → `fact_payments.order_id`

- `fact_orders.order_id`
  → `fact_reviews.order_id`

- `dim_product.product_id`
  → `fact_order_items.product_id`

- `dim_seller.seller_id`
  → `fact_order_items.seller_id`

- `dim_date.date`
  → order purchase date in `fact_orders`

- `dim_geography.zip_code_prefix`
  → customer and seller zip-code prefixes where appropriate

---

# Relationship Cardinality

The expected relationship patterns include:

## Customer to Orders

One customer record can connect to one order record through `customer_id`
in the source model.

Customer-level analytics across multiple purchases will additionally use
`customer_unique_id`.

## Orders to Order Items

One order can contain many order items.

Relationship:

`fact_orders (1) -> fact_order_items (many)`

## Orders to Payments

One order can contain multiple payment records.

Relationship:

`fact_orders (1) -> fact_payments (many)`

## Orders to Reviews

An order can have one or more review records in the source data.

Relationship:

`fact_orders (1) -> fact_reviews (many)`

## Products to Order Items

One product can appear in many order-item transactions.

Relationship:

`dim_product (1) -> fact_order_items (many)`

## Sellers to Order Items

One seller can participate in many order-item transactions.

Relationship:

`dim_seller (1) -> fact_order_items (many)`

---

# Grain Protection

Measures must be calculated at the grain of the relevant fact table.

Examples:

### Sales Revenue

Use:

`fact_order_items.price`

because item price exists at the order-item grain.

### Payment Value

Use:

`fact_payments.payment_value`

because payment values exist at the payment-record grain.

### Total Orders

Use:

`fact_orders.order_id`

because the Orders fact has one row per order.

### Review Score

Use:

`fact_reviews.review_score`

because review scores exist at the review-record grain.

Mixing these measures in uncontrolled joins could produce duplicated values.

---

# Initial Analytical Model

Conceptually, the model will resemble:

                    dim_customer
                         |
                         |
                     fact_orders
                    /     |      \
                   /      |       \
        fact_order_items  |    fact_reviews
              |           |
              |       fact_payments
          /       \
         /         \
 dim_product     dim_seller


Additional reusable dimensions:

- dim_date
- dim_geography

---

# Next Phase

The next phase will implement the analytical model through data
transformations.

The transformation layer will:

1. Clean and standardize source data.
2. Convert timestamps to appropriate datetime types.
3. Resolve documented data-quality issues.
4. Build analytics-ready dimension tables.
5. Build fact tables while preserving source grain.
6. Create derived operational metrics and flags.
7. Validate row counts and referential relationships.