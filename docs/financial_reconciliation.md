# Financial Reconciliation

## Purpose

This analysis validates the relationship between item-level transaction values
and payment-level transaction values while respecting the different grains of
the two fact tables.

The objective is not to force both datasets to contain identical totals, but to
identify and explain differences in order coverage and transaction values.

---

## Fact Table Grains

### fact_order_items

Grain:

`order_id + order_item_id`

One row represents one item position within an order.

Financial measures include:

- price
- freight_value
- item_total_value

### fact_payments

Grain:

`order_id + payment_sequential`

One row represents one payment sequence associated with an order.

Financial measure:

- payment_value

Because the two fact tables operate at different grains, they must not be
joined directly for financial reconciliation.

Both datasets were first aggregated to one row per `order_id`.

---

## Order Coverage

Orders represented in `fact_order_items`:

**98,666**

Orders represented in `fact_payments`:

**99,440**

After performing a full outer comparison at the order grain:

| Coverage | Orders |
|---|---:|
| Present in both facts | 98,665 |
| Payments but no order items | 775 |
| Order items but no payments | 1 |

---

## Payment-Only Orders

The 775 orders containing payment activity but no order-item records had the
following order statuses:

| Order Status | Orders |
|---|---:|
| unavailable | 603 |
| canceled | 164 |
| created | 5 |
| invoiced | 2 |
| shipped | 1 |

This indicates that differences in financial totals are partly caused by
different business populations represented by the two fact tables.

Payment activity can exist for orders that did not progress into the
order-item population in the same way as successfully processed orders.

---

## Matched Order Reconciliation

Orders present in both financial fact tables:

**98,665**

Orders where payment value and item-plus-freight value reconcile within
$0.01:

**98,290**

Matched orders containing financial differences:

**375**

The remaining mismatches should be treated as an analytical investigation
population rather than automatically modified or removed.

---

## Overall Financial Totals

Total item price plus freight value:

**15,843,553.24**

Total payment value:

**16,008,872.12**

Overall difference:

**165,318.88**

The overall difference should not be interpreted as a direct financial error
because the underlying fact tables contain different order populations and
operate at different transactional grains.

---

## Modeling Decision

Financial measures will remain separated by business grain.

### Merchandise and Freight Analysis

Use:

`fact_order_items`

Measures:

- price
- freight_value
- item_total_value

### Payment Analysis

Use:

`fact_payments`

Measures:

- payment_value
- payment_type
- payment_installments

Payment values will not be directly joined to individual order-item rows.

When reconciliation or cross-fact analysis is required, both datasets will
first be aggregated to a common order grain.

---

## Key Finding

The reconciliation demonstrates that the majority of orders represented in
both financial facts align successfully, while differences arise from both
order-population coverage and a smaller subset of matched orders requiring
further investigation.

This validates the decision to preserve separate fact-table grains in the
analytical model.