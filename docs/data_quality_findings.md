# Data Quality Findings

## Orders Dataset

### Finding 1 — Missing Lifecycle Timestamps

The orders dataset contains missing values in several lifecycle timestamp fields:

- `order_approved_at`
- `order_delivered_carrier_date`
- `order_delivered_customer_date`

Many missing timestamps may represent valid business states because canceled,
unavailable, processing, invoiced, or newly created orders may not have reached
later stages of the order lifecycle.

### Finding 2 — Delivered Orders Missing Carrier Timestamp

Two orders with `order_status = delivered` have a missing
`order_delivered_carrier_date`.

These records represent potential data-quality anomalies because a delivered
order would normally be expected to have been handed to a carrier.

One of these delivered records also has a missing customer delivery timestamp,
which requires additional investigation.

### Proposed Treatment

- Preserve the original records in the raw data layer.
- Do not automatically delete records containing missing lifecycle timestamps.
- Distinguish expected business-state nulls from inconsistent lifecycle records.
- Exclude inconsistent records only from KPIs that require the missing timestamp,
  while retaining them for other valid analyses where appropriate.

  ### Finding 3 — Delivered Orders Missing Customer Delivery Timestamp

Eight orders with `order_status = delivered` have a missing
`order_delivered_customer_date`.

Most missing customer delivery timestamps correspond to orders that have not
reached the delivered stage, such as shipped, canceled, unavailable,
processing, invoiced, created, or approved orders.

The eight delivered orders represent potential lifecycle inconsistencies because
a completed delivery would normally be expected to include an actual customer
delivery timestamp.

### Finding 4 — Delivered Orders Missing Approval Timestamp

Fourteen orders with `order_status = delivered` have a missing
`order_approved_at` timestamp.

Canceled and newly created orders may reasonably lack approval timestamps, but
delivered orders would normally be expected to have passed through an approval
stage.

These records should therefore be retained but flagged as potential
data-quality anomalies.

### Orders Dataset Profiling Summary

- Total orders: 99,441
- Unique order IDs: 99,441
- Duplicate rows: 0
- Table grain: one row represents one order
- `order_id` is a candidate primary key
- Most lifecycle timestamp nulls are consistent with incomplete or canceled
  order states
- A small number of delivered orders contain inconsistent or missing lifecycle
  timestamps and require controlled treatment in downstream KPIs