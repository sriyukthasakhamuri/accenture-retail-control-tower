# Enterprise Retail Analytics & Operations Control Tower

## Dashboard Design Specification

The dashboard is designed to provide executive, commercial,
operational, customer, and risk visibility across the retail marketplace.

---

# Page 1 — Executive Overview

## Business Question

How is the marketplace performing overall?

## KPI Cards

- Total Orders
- Delivered Orders
- Unique Customers
- Active Sellers
- Merchandise Value
- Total Payment Value
- Average Order Value
- Average Review Score
- Late Delivery Rate

## Visuals

### Monthly Revenue Trend
Shows payment value and merchandise value over time.

### Monthly Order Volume
Shows order volume by month.

### Delivery Performance
Compares:
- On Time / Early
- Late
- Not Delivered

### Customer Satisfaction
Shows:
- Average Review Score
- Positive Review Rate
- Negative Review Rate

## Key Management Insight

Late deliveries should be monitored because they are strongly
associated with lower customer satisfaction.

---

# Page 2 — Sales & Product Performance

## Business Question

Which products and categories generate the most commercial value?

## KPI Cards

- Merchandise Value
- Items Sold
- Freight Value
- Average Item Price

## Visuals

### Top Product Categories by Revenue

Bar chart:
- Product Category
- Merchandise Value

### Product Category Order Volume

Bar chart:
- Product Category
- Orders

### Revenue vs Delivery Risk

Scatter plot:

X-axis:
- Merchandise Value

Y-axis:
- Late Delivery Rate

Bubble size:
- Orders

Category:
- Product Category

### Product Category Customer Satisfaction

Table:

- Product Category
- Orders
- Merchandise Value
- Average Review Score
- Negative Review Rate
- Late Delivery Rate

## Management Question

Which commercially important categories also have poor operational
or customer-experience performance?

---

# Page 3 — Delivery & Operations

## Business Question

Where are operational delivery problems occurring?

## KPI Cards

- Delivered Orders
- Late Delivery Rate
- Average Delivery Time
- Average Review Score

## Visuals

### On-Time vs Late Delivery

Column chart:
- Delivery Status
- Orders

### Delivery Status vs Review Score

Bar chart:
- Delivery Status
- Average Review Score

### Negative Review Rate by Delivery Status

Bar chart:
- Delivery Status
- Negative Review Rate

### Monthly Late Delivery Trend

Line chart:
- Month
- Late Delivery Rate

## Key Insight

Validated dataset result:

On Time / Early Orders:
- Average Review Score: 4.29
- Negative Review Rate: 9.19%

Late Orders:
- Average Review Score: 2.57
- Negative Review Rate: 53.99%

Late deliveries were strongly associated with significantly
lower customer satisfaction.

---

# Page 4 — Customer & Payment Behavior

## Business Question

How do customers purchase and how do they pay?

## KPI Cards

- Unique Customers
- Repeat Customers
- Repeat Customer Rate
- Average Order Value
- Total Payment Value

## Customer Visuals

### Customer Type

Donut chart:
- One-Time Customer
- Repeat Customer

### Customer Frequency Segment

Bar chart:
- 1 Order
- 2–3 Orders
- 4–5 Orders
- 6+ Orders

### Customer Value

Table:
- Customer Type
- Customers
- Total Orders
- Average Customer Value
- Average Review Score

## Payment Visuals

### Payment Value by Method

Bar chart:
- Payment Type
- Total Payment Value

### Payment Value Share

Donut chart:
- Credit Card
- Boleto
- Voucher
- Debit Card

### Installment Behavior

Bar chart:
- Payment Type
- Average Installments

## Key Customer Finding

Unique Customers:
96,096

One-Time Customers:
93,099

Repeat Customers:
2,997

Repeat Customer Rate:
3.12%

The repeat-customer rate describes purchasing behavior within
the available dataset observation period and should not be interpreted
as a long-term retention rate.

---

# Page 5 — Geographic & Risk Control Tower

## Business Question

Where should management investigate first?

## Geographic Visuals

### State Revenue Map

Location:
- Customer State

Value:
- Merchandise Value

### State Operational Performance

Table:
- State
- Orders
- Merchandise Value
- Late Delivery Rate
- Average Review Score

### Revenue vs Delivery Risk by State

Scatter plot:

X-axis:
- Merchandise Value

Y-axis:
- Late Delivery Rate

Bubble size:
- Orders

## Operational Risk Visuals

### High-Priority Entities

Table:

- Entity Type
- Entity Name
- Management Priority
- Operational Risk Score
- Orders
- Merchandise Value
- Late Delivery Rate
- Negative Review Rate

### Risk Distribution

Stacked chart:

Axis:
- Entity Type

Legend:
- High Priority
- Watch
- Monitor

Values:
- Entity Count

## Risk Classification Results

Customer States:
- High Priority: 3
- Watch: 6
- Monitor: 18

Product Categories:
- High Priority: 6
- Watch: 15
- Monitor: 53

Sellers:
- High Priority: 197
- Watch: 710
- Monitor: 2,188

## Overall Operational Benchmarks

Late Delivery Rate:
8.11%

Average Review Score:
4.09

Negative Review Rate:
14.64%

## Risk Score Methodology

Operational Risk Score:

25% Order Volume Exposure
+
25% Revenue Exposure
+
25% Late Delivery Risk
+
25% Negative Review Risk

The score is a portfolio-designed management prioritization metric
and is not an official source-system metric.

---

# Dashboard Navigation

Recommended navigation:

1. Executive Overview
2. Sales & Products
3. Delivery Operations
4. Customers & Payments
5. Geographic Risk Control Tower

---

# Dashboard Design Principles

- Executive-friendly layout
- Limited visual clutter
- Clear KPI hierarchy
- Consistent metric definitions
- Business questions drive visual selection
- Avoid misleading causal claims
- Use validated SQL outputs
- Highlight exceptions and management priorities
- Maintain consistent filters across dashboard pages

---

# Global Dashboard Filters

Recommended slicers:

- Date
- Customer State
- Product Category
- Seller State
- Delivery Status

Filters should be synchronized across pages where appropriate.