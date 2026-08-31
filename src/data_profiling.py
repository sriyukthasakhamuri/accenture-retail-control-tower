from pathlib import Path
import pandas as pd
RAW_DATA_PATH = Path("data/raw")
csv_files = list(RAW_DATA_PATH.glob("*.csv"))

print(f"Found {len(csv_files)} CSV files:")

for file_path in csv_files:
    print(file_path.name)

orders_file = RAW_DATA_PATH / "olist_orders_dataset.csv"

orders_df = pd.read_csv(orders_file)
print("\nOrders dataset shape:")
print(orders_df.shape)
print("\nOrders columns:")
print(orders_df.columns.tolist())
print("\nFirst 5 rows:")
print(orders_df.head())
print("\nData types:")
print(orders_df.dtypes)
print("\nMissing values:")
print(orders_df.isna().sum())
print("\nDuplicate rows:")
print(orders_df.duplicated().sum())
print("\nUnique order IDs:")
print(orders_df["order_id"].nunique())
print("\nOrder status distribution:")
print(orders_df["order_status"].value_counts())
print("\nMissing delivery dates by order status:")

missing_delivery_by_status = (
    orders_df[
        orders_df["order_delivered_customer_date"].isna()
    ]["order_status"]
    .value_counts()
)

print(missing_delivery_by_status)

print("\nMissing approval dates by order status:")

missing_approval_by_status = (
    orders_df[
        orders_df["order_approved_at"].isna()
    ]["order_status"]
    .value_counts()
)

print(missing_approval_by_status)

print("\nMissing carrier dates by order status:")

missing_carrier_by_status = (
    orders_df[
        orders_df["order_delivered_carrier_date"].isna()
    ]["order_status"]
    .value_counts()
)

print(missing_carrier_by_status)

print("\nDelivered orders missing carrier date:")

delivered_missing_carrier = orders_df[
    (orders_df["order_status"] == "delivered")
    & (orders_df["order_delivered_carrier_date"].isna())
]

print(delivered_missing_carrier)