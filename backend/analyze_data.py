import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "cleaned_orders.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

print("\nOverall RTO rate:")
print(df["final_status"].value_counts(normalize=True) * 100)

print("\nRTO rate by previous RTO count:")
history = df.groupby("customer_prior_rto")["final_status"].value_counts(normalize=True) * 100
print(history)

print("\nRTO rate by previous orders count:")
prior_orders = df.groupby("customer_prior_orders")["final_status"].value_counts(normalize=True) * 100
print(prior_orders)

print("\nRTO rate by address quality:")
address = df.groupby("address_quality")["final_status"].value_counts(normalize=True) * 100
print(address)

print("\nRTO rate by suspicious name:")
suspicious = df.groupby("suspicious_name")["final_status"].value_counts(normalize=True) * 100
print(suspicious)

print("\nRTO rate by invalid phone:")
phone = df.groupby("invalid_phone")["final_status"].value_counts(normalize=True) * 100
print(phone)

print("\nRTO rate by city:")
city = df.groupby("city")["final_status"].value_counts(normalize=True) * 100
print(city.sort_values(ascending=False).head(20))

print("\nRTO rate by courier:")
courier = df.groupby("courier")["final_status"].value_counts(normalize=True) * 100
print(courier)

print("\nRTO rate by acquisition source:")
source = df.groupby("utm_source")["final_status"].value_counts(normalize=True) * 100
print(source)

print("\nRTO rate by order value:")
df["value_bucket"] = pd.cut(
    df["order_value"],
    bins=[0, 500, 1000, 1500, 2000, 10000],
    labels=["0-500", "501-1000", "1001-1500", "1501-2000", "2000+"]
)
value = df.groupby("value_bucket")["final_status"].value_counts(normalize=True) * 100
print(value)