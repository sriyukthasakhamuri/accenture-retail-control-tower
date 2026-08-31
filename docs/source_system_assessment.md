# Source System Assessment

## Purpose

This document summarizes the structure, grain, candidate keys, business purpose,
and notable data-quality characteristics of the source datasets used in the
Enterprise Retail Analytics & Operations Control Tower project.

The assessment was produced using automated Python profiling and candidate-key
validation before designing downstream transformations or analytical models.

---

## Source Dataset Summary

| Dataset | Rows | Grain | Candidate Key | Purpose |
|---|---:|---|---|---|
| Customers | 99,441 | One order-level customer record | `customer_id` | Customer identity and geographic attributes |
| Orders | 99,441 | One order | `order_id` | Order lifecycle and fulfillment timestamps |
| Order Items | 112,650 | One item position within an order | `order_id + order_item_id` | Product, seller, price, and freight information |
| Payments | 103,886 | One payment sequence for an order | `order_id + payment_sequential` | Payment method, installments, and payment value |
| Reviews | 99,224 | One review record associated with an order | `review_id + order_id` | Customer satisfaction and review information |
| Products | 32,951 | One product | `product_id` | Product attributes and category information |
| Sellers | 3,095 | One seller | `seller_id` | Seller identity and geographic attributes |
| Geolocation | 1,000,163 | One geographic coordinate observation | No simple unique key identified | Zip-code-prefix geographic reference data |
| Category Translation | 71 | One category translation mapping | `product_category_name` | Portuguese-to-English product category mapping |

---

## 1. Customers

**Dataset:** `olist_customers_dataset.csv`

**Rows:** 99,441

### Grain

One row represents an order-level customer record.

### Candidate Key

`customer_id`

Python validation showed:

- Total rows: 99,441
- Unique `customer_id` values: 99,441
- Duplicate candidate keys: 0

Therefore, `customer_id` uniquely identifies each row.

### Customer Identity Observation

The dataset contains:

- 99,441 unique `customer_id` records
- 96,096 unique `customer_unique_id` values

This indicates that `customer_id` and `customer_unique_id` serve different
analytical purposes.

`customer_id` identifies the customer record associated with an order, while
`customer_unique_id` can be used to identify repeat purchasing behavior across
multiple orders.

This distinction will be important for customer-level metrics such as:

- Repeat customer rate
- Orders per customer
- Customer purchase frequency
- Customer lifetime value

---

## 2. Orders

**Dataset:** `olist_orders_dataset.csv`

**Rows:** 99,441

### Grain

One row represents one order.

### Candidate Key

`order_id`

Validation showed:

- Total rows: 99,441
- Unique `order_id` values: 99,441
- Duplicate rows: 0

Therefore, `order_id` is a strong candidate primary key.

### Business Role

The Orders dataset provides the central order lifecycle, including:

- Customer association
- Order status
- Purchase timestamp
- Approval timestamp
- Carrier handoff timestamp
- Customer delivery timestamp
- Estimated delivery date

### Data Quality Notes

Missing lifecycle timestamps occur primarily for orders that have not completed
the full fulfillment lifecycle.

However, a small number of delivered orders contain missing approval, carrier,
or customer-delivery timestamps and have been flagged as potential data-quality
anomalies.

Detailed findings are documented in `data_quality_findings.md`.

---

## 3. Order Items

**Dataset:** `olist_order_items_dataset.csv`

**Rows:** 112,650

### Grain

One row represents one item position within an order.

### Candidate Key Testing

`order_id` alone is not unique.

Python validation found:

- Total rows: 112,650
- Unique `order_id` values: 98,666

This confirms that an order can contain multiple order-item records.

The combination:

`order_id + order_item_id`

produced:

- 112,650 unique combinations
- 0 rows involved in duplicate candidate keys

Therefore the candidate composite key is:

`(order_id, order_item_id)`

### Business Role

This dataset connects orders to:

- Products
- Sellers
- Item prices
- Freight values

It will be a major transactional source for sales and seller analytics.

---

## 4. Payments

**Dataset:** `olist_order_payments_dataset.csv`

**Rows:** 103,886

### Grain

One row represents one payment sequence associated with an order.

### Candidate Key Testing

`order_id` alone is not unique because one order can contain multiple payment
records.

The combination:

`order_id + payment_sequential`

was unique across all 103,886 rows.

Therefore the candidate composite key is:

`(order_id, payment_sequential)`

### Business Role

The Payments dataset supports analysis of:

- Payment methods
- Installment usage
- Payment values
- Multiple-payment behavior

---

## 5. Reviews

**Dataset:** `olist_order_reviews_dataset.csv`

**Rows:** 99,224

### Grain

One row represents one review record associated with an order.

### Candidate Key Testing

Neither field was individually unique:

- `review_id` was not unique
- `order_id` was not unique

The combination:

`review_id + order_id`

produced:

- 99,224 unique combinations
- 0 rows involved in duplicate candidate keys

Therefore the candidate composite key is:

`(review_id, order_id)`

### Business Role

The Reviews dataset supports analysis of:

- Customer satisfaction
- Review scores
- Written feedback
- Relationship between delivery performance and satisfaction

### Data Quality Note

The profiling process identified substantial missing values concentrated in two
review-related columns.

These should be investigated based on whether the fields represent optional
written review content before any missing-value treatment is applied.

---

## 6. Products

**Dataset:** `olist_products_dataset.csv`

**Rows:** 32,951

### Grain

One row represents one product.

### Candidate Key

`product_id`

Validation showed:

- Total rows: 32,951
- Unique `product_id` combinations: 32,951
- Duplicate candidate keys: 0

Therefore `product_id` uniquely identifies each product.

### Business Role

The Products dataset provides attributes used for:

- Product category analysis
- Product-level sales analysis
- Product dimensions and characteristics

### Data Quality Note

Eight product columns contain at least some missing values.

These missing attributes will be investigated before transformation rules are
defined.

---

## 7. Sellers

**Dataset:** `olist_sellers_dataset.csv`

**Rows:** 3,095

### Grain

One row represents one seller.

### Candidate Key

`seller_id`

Validation showed:

- Total rows: 3,095
- Unique `seller_id` combinations: 3,095
- Duplicate candidate keys: 0

Therefore `seller_id` uniquely identifies each seller.

### Business Role

The Sellers dataset supports:

- Seller performance analysis
- Seller geographic analysis
- Seller delivery-performance comparisons

---

## 8. Geolocation

**Dataset:** `olist_geolocation_dataset.csv`

**Rows:** 1,000,163

### Grain

One row represents a geographic coordinate observation associated with a
zip-code prefix.

### Profiling Results

The dataset contains:

- 1,000,163 total rows
- 19,015 unique zip-code prefixes
- 261,831 exact duplicate rows

Therefore:

`geolocation_zip_code_prefix`

is not a unique key.

### Data Quality Consideration

The large number of exact duplicate records requires controlled treatment.

Duplicates should not be removed blindly until the intended analytical use of
the geolocation table is defined.

For dimensional analytics, the data may later need to be aggregated to one
representative geographic record per zip-code prefix.

---

## 9. Product Category Translation

**Dataset:** `product_category_name_translation.csv`

**Rows:** 71

### Grain

One row represents one product-category translation mapping.

### Candidate Key

`product_category_name`

Validation showed:

- Total rows: 71
- Unique candidate-key combinations: 71
- Duplicate candidate keys: 0

Therefore `product_category_name` uniquely identifies each translation record.

### Business Role

This dataset translates product category names into English and can be joined
to the Products dataset using `product_category_name`.

---

# Source Relationships

The initial source-system analysis suggests the following primary relationships:

- Customers → Orders using `customer_id`
- Orders → Order Items using `order_id`
- Orders → Payments using `order_id`
- Orders → Reviews using `order_id`
- Order Items → Products using `product_id`
- Order Items → Sellers using `seller_id`
- Products → Category Translation using `product_category_name`
- Customer and Seller geography can be enriched using zip-code-prefix data from
  Geolocation

These relationships will be validated further before implementing the analytical
data model.

---

# Key Modeling Observations

The source assessment identified several important modeling considerations:

1. Orders are the central business transaction.
2. Orders can contain multiple order items.
3. Orders can contain multiple payment records.
4. Review records do not have a reliable single-column candidate key.
5. `customer_unique_id` should be considered for repeat-customer analytics.
6. Geolocation requires transformation before it can safely behave as a
   dimension table.
7. Raw lifecycle nulls should not automatically be treated as data defects.
8. Analytical joins must respect the grain of each source table to avoid
   duplicate counting.

---

# Next Step

The next phase will translate these source-system relationships into an
analytical data model suitable for SQL transformations, KPI development, and
Power BI reporting.