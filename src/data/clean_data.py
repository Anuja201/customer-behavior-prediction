from pathlib import Path
import pandas as pd

from load_data import load_data


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_PATH = PROCESSED_DIR / "cleaned_retail.csv"


def clean_data(df):

    print("\nStarting data cleaning...")

    # Make a copy so the original dataframe is not modified
    df = df.copy()

    # Standardize column names
    df.columns = [
        str(column).strip().replace(" ", "_")
        for column in df.columns
    ]

    print("\nColumns after standardization:")
    print(df.columns.tolist())

    # Remove completely empty rows
    before = len(df)

    df = df.dropna(how="all")

    print(f"\nRemoved completely empty rows: {before - len(df)}")

    # Remove duplicate transactions
    before = len(df)

    df = df.drop_duplicates()

    print(f"Removed duplicate rows: {before - len(df)}")

    # Convert Customer ID to string
    if "Customer_ID" in df.columns:
        df["Customer_ID"] = df["Customer_ID"].astype("Int64").astype(str)

    # Convert InvoiceDate to datetime
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(
            df["InvoiceDate"],
            errors="coerce"
        )

    # Convert Quantity to numeric
    if "Quantity" in df.columns:
        df["Quantity"] = pd.to_numeric(
            df["Quantity"],
            errors="coerce"
        )

    # Convert Price to numeric
    if "Price" in df.columns:
        df["Price"] = pd.to_numeric(
            df["Price"],
            errors="coerce"
        )

    # Remove rows with invalid essential values
    required_columns = [
        column
        for column in ["Customer_ID", "InvoiceDate", "Quantity", "Price"]
        if column in df.columns
    ]

    before = len(df)

    if required_columns:
        df = df.dropna(subset=required_columns)

    print(f"Removed rows with missing essential values: {before - len(df)}")

    # Remove transactions with zero or negative quantity
    if "Quantity" in df.columns:
        before = len(df)

        df = df[df["Quantity"] > 0]

        print(
            f"Removed invalid quantities: "
            f"{before - len(df)}"
        )

    # Remove transactions with zero or negative price
    if "Price" in df.columns:
        before = len(df)

        df = df[df["Price"] > 0]

        print(
            f"Removed invalid prices: "
            f"{before - len(df)}"
        )

    # Create transaction amount
    if "Quantity" in df.columns and "Price" in df.columns:
        df["Total_Amount"] = df["Quantity"] * df["Price"]

    # Remove rows without customer ID
    if "Customer_ID" in df.columns:
        before = len(df)

        df = df[
            (df["Customer_ID"] != "nan") &
            (df["Customer_ID"] != "<NA>")
        ]

        print(
            f"Removed rows without customer ID: "
            f"{before - len(df)}"
        )

    print("\nCleaning completed.")
    print(f"Final rows: {len(df)}")
    print(f"Final columns: {len(df.columns)}")

    return df


def save_clean_data(df):
    """Save cleaned data as CSV."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_PATH,
        index=False
    )

    print(
        f"\nCleaned dataset saved to:\n"
        f"{PROCESSED_PATH}"
    )


if __name__ == "__main__":

    # Load raw dataset
    raw_df = load_data()

    # Clean dataset
    cleaned_df = clean_data(raw_df)

    # Save dataset
    save_clean_data(cleaned_df)

    print("\nFirst 5 cleaned rows:")
    print(cleaned_df.head())