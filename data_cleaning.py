"""Reusable data cleaning functions for the sales automation project."""
from pathlib import Path
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "Order_ID", "Order_Date", "Customer_ID", "Product", "Category", "Region",
    "Sales_Channel", "Quantity", "Unit_Price", "Discount", "Sales_Amount"
]

def load_data(path):
    """Load a CSV file and validate required columns."""
    df = pd.read_csv(path)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")
    return df

def clean_sales_data(df):
    """Return (cleaned_df, quality_metrics). Cleaning decisions are explicit."""
    data = df.copy()
    rows_before = len(data)
    duplicate_rows = int(data.duplicated().sum())

    # Normalize whitespace and case for text fields.
    text_cols = ["Order_ID", "Customer_ID", "Product", "Category", "Region", "Sales_Channel"]
    for col in text_cols:
        data[col] = data[col].astype("string").str.strip()
        data[col] = data[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    # Consistent title case for categories and labels.
    for col in ["Product", "Category", "Region", "Sales_Channel"]:
        data[col] = data[col].str.title()

    # Parse dates and numeric fields safely.
    data["Order_Date"] = pd.to_datetime(data["Order_Date"], errors="coerce")
    numeric_cols = ["Quantity", "Unit_Price", "Discount", "Sales_Amount"]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    missing_before = int(data.isna().sum().sum())
    invalid_quantity = int((data["Quantity"] <= 0).fillna(False).sum())
    invalid_price = int((data["Unit_Price"] <= 0).fillna(False).sum())
    invalid_discount = int(((data["Discount"] < 0) | (data["Discount"] > 1)).fillna(False).sum())

    # Drop exact duplicate rows first.
    data = data.drop_duplicates().copy()

    # Invalid quantities/prices are unknown/bad records; mark as missing then drop rows
    # where core transaction metrics cannot be recovered.
    data.loc[data["Quantity"] <= 0, "Quantity"] = np.nan
    data.loc[data["Unit_Price"] <= 0, "Unit_Price"] = np.nan
    data.loc[(data["Discount"] < 0) | (data["Discount"] > 1), "Discount"] = np.nan

    # Fill category-like fields with a visible label; do not fabricate customer IDs.
    for col in ["Region", "Sales_Channel", "Category", "Product"]:
        data[col] = data[col].fillna("Unknown")

    # Numeric imputation: median for price; 0 for discount; quantity missing rows removed.
    data["Unit_Price"] = data["Unit_Price"].fillna(data["Unit_Price"].median())
    data["Discount"] = data["Discount"].fillna(0)
    data = data.dropna(subset=["Order_ID", "Order_Date", "Quantity"]).copy()
    data["Quantity"] = data["Quantity"].astype(int)

    # Recalculate sales to avoid stale or inconsistent values.
    data["Sales_Amount"] = (data["Quantity"] * data["Unit_Price"] * (1 - data["Discount"])).round(2)

    # Customer IDs remain missing as Unknown to preserve transaction rows without inventing identities.
    data["Customer_ID"] = data["Customer_ID"].fillna("Unknown")
    data["Unit_Price"] = data["Unit_Price"].round(2)
    data["Discount"] = data["Discount"].round(4)
    data["Order_Date"] = data["Order_Date"].dt.strftime("%Y-%m-%d")

    # Quality metrics
    missing_after = int(data.isna().sum().sum())
    metrics = {
        "rows_before": rows_before,
        "rows_after": len(data),
        "duplicate_rows_removed": duplicate_rows,
        "missing_cells_before_cleaning": missing_before,
        "missing_cells_after_cleaning": missing_after,
        "invalid_quantity_records": invalid_quantity,
        "invalid_unit_price_records": invalid_price,
        "invalid_discount_records": invalid_discount,
        "rows_removed_total": rows_before - len(data),
        "data_completeness_after_pct": round(100 * (1 - missing_after / max(data.size, 1)), 2),
    }
    return data, metrics
