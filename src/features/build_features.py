from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_retail.csv"
FEATURES_DIR = PROJECT_ROOT / "data" / "processed"
FEATURES_PATH = FEATURES_DIR / "customer_features.csv"

def build_features():
    print("Loading cleaned dataset...")
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(f"Cleaned data not found at {PROCESSED_PATH}. Run clean_data.py first.")
    
    df = pd.read_csv(PROCESSED_PATH)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    
    min_date = df["InvoiceDate"].min()
    max_date = df["InvoiceDate"].max()
    
    print(f"Dataset Date Range: {min_date.date()} to {max_date.date()}")
    
    # To create a proper churn label, let's split the timeline in half or use a robust window.
    # For instance, first 70% of days for feature building, last 30% for churn observation.
    total_days = (max_date - min_date).days
    cutoff_days = int(total_days * 0.7)
    cutoff_date = min_date + pd.Timedelta(days=cutoff_days)
    
    print(f"Feature History Cutoff Date: {cutoff_date.date()}")
    
    # Split data into history (features) and future (churn evaluation)
    history_df = df[df["InvoiceDate"] <= cutoff_date]
    future_df = df[df["InvoiceDate"] > cutoff_date]
    
    # Customers active in the history period
    history_customers = set(history_df["Customer_ID"].dropna().astype(str).unique())
    # Customers active in the future window
    active_future_customers = set(future_df["Customer_ID"].dropna().astype(str).unique())
    
    print("\nBuilding customer-level features from history period...")
    
    # Aggregate features per customer from history
    customer_features = history_df.groupby("Customer_ID").agg(
        recency_days=("InvoiceDate", lambda x: (cutoff_date - x.max()).days),
        frequency=("Invoice", "nunique"),
        monetary=("Total_Amount", "sum"),
        avg_basket_size=("Quantity", "mean"),
        avg_item_price=("Price", "mean")
    ).reset_index()
    
    # Define churn label: 1 if customer from history did NOT make a purchase in the future window, else 0
    customer_features["churn"] = customer_features["Customer_ID"].apply(
        lambda cid: 0 if cid in active_future_customers else 1
    )
    
    customer_features["clv_proxy"] = customer_features["monetary"]
    
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    customer_features.to_csv(FEATURES_PATH, index=False)
    
    print(f"Customer features saved to {FEATURES_PATH}")
    print(f"Total customers processed: {len(customer_features)}")
    print(f"Churn rate in feature set: {customer_features['churn'].mean():.2%}")
    
    return customer_features

if __name__ == "__main__":
    build_features()