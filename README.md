# Retail Analytics Control Tower

An end-to-end retail analytics project built to analyze sales, customer behavior, delivery performance, payment patterns, geographic trends, and operational risk.

## Project Overview

This project transforms raw e-commerce data into an analytics-ready model using Python, SQL, DuckDB, and Power BI.

The goal is to provide a management-level control tower for monitoring:

- Sales performance
- Customer behavior
- Delivery operations
- Product and seller performance
- Payment behavior
- Geographic trends
- Operational risk

## Tech Stack

- Python
- Pandas
- SQL
- DuckDB
- Power BI
- Git / GitHub

## Project Architecture

Raw CSV Data  
↓  
Python Data Processing  
↓  
Dimensional Modeling  
↓  
DuckDB Analytics Layer  
↓  
SQL Business Analysis  
↓  
Power BI Dashboard

## Key Business KPIs

- Total Orders: 99,441
- Delivered Orders: 96,478
- Unique Customers: 96,096
- Active Sellers: 3,095
- Total Payment Value: $16.01M
- Average Order Value: $160.99
- Average Delivery Time: 12.56 days
- Late Delivery Rate: 8.11%
- Average Review Score: 4.09
- Negative Review Rate: 14.64%

## Key Insights

- Late deliveries were strongly associated with lower customer satisfaction.
- Late orders had an average review score of approximately 2.57 compared with 4.29 for on-time or early deliveries.
- Negative review rates were significantly higher for late deliveries.
- Credit cards accounted for the majority of payment value.
- Repeat customer rate was approximately 3.12%.
- Revenue and order activity were heavily concentrated in a small number of states.
- Operational risk scoring was used to identify high-priority entities across sellers, product categories, and customer states.

## Dashboard Pages

### 1. Executive Overview

![Executive Overview](dashboards/screenshots/01_executive_overview.png)

### 2. Sales & Product Performance

![Sales & Product Performance](dashboards/screenshots/02_sales_product_performance.png)

### 3. Delivery & Operations

![Delivery & Operations](dashboards/screenshots/03_delivery_operations.png)

### 4. Customer & Payment Behavior

![Customer & Payment Behavior](dashboards/screenshots/04_customer_payment_behavior.png)

### 5. Geographic & Risk Control Tower

![Geographic & Risk Control Tower](dashboards/screenshots/05_geographic_risk_control_tower.png)

## Data Modeling

The analytics layer uses fact and dimension tables including:

- fact_orders
- fact_order_items
- fact_payments
- fact_reviews
- dim_customer
- dim_product
- dim_seller
- dim_geography
- dim_date

## SQL Analysis

The SQL layer includes:

- Executive KPIs
- Monthly performance
- Product performance
- Seller performance
- Geographic performance
- Customer behavior
- Payment behavior
- Delivery operations
- Operational risk prioritization

## Operational Risk Model

A risk-prioritization model was created using:

- Revenue exposure
- Order volume exposure
- Late delivery performance
- Negative review performance

Entities were categorized into:

- High Priority
- Watch
- Monitor

## Repository Structure

```text
dashboards/
data/
docs/
notebooks/
sql/
src/
tests/
README.md
requirements.txt