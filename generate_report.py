"""Create data quality, sales summary, and visual report files."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from data_cleaning import clean_sales_data, load_data

def build_reports(raw_path, output_dir):
    output_dir = Path(output_dir)
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    raw = load_data(raw_path)
    cleaned, metrics = clean_sales_data(raw)
    cleaned_path = output_dir.parent / "data" / "cleaned_sales_data.csv"
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(cleaned_path, index=False)

    quality = pd.DataFrame([
        {"Metric": k, "Value": v} for k, v in metrics.items()
    ])
    quality.to_csv(output_dir / "data_quality_report.csv", index=False)

    monthly = cleaned.copy()
    monthly["Order_Date"] = pd.to_datetime(monthly["Order_Date"])
    monthly["Month"] = monthly["Order_Date"].dt.to_period("M").astype(str)
    monthly_summary = monthly.groupby("Month", as_index=False).agg(
        Total_Sales=("Sales_Amount", "sum"),
        Total_Orders=("Order_ID", "nunique"),
        Units_Sold=("Quantity", "sum")
    )
    monthly_summary.to_csv(output_dir / "monthly_sales_summary.csv", index=False)

    product_summary = cleaned.groupby("Product", as_index=False).agg(
        Total_Sales=("Sales_Amount", "sum"),
        Units_Sold=("Quantity", "sum"),
        Order_Count=("Order_ID", "nunique")
    ).sort_values("Total_Sales", ascending=False)
    product_summary.to_csv(output_dir / "product_sales_summary.csv", index=False)

    region_summary = cleaned.groupby("Region", as_index=False).agg(
        Total_Sales=("Sales_Amount", "sum"),
        Order_Count=("Order_ID", "nunique")
    ).sort_values("Total_Sales", ascending=False)
    region_summary.to_csv(output_dir / "region_sales_summary.csv", index=False)

    # Text/JSON executive summary
    total_sales = float(cleaned["Sales_Amount"].sum())
    total_orders = int(cleaned["Order_ID"].nunique())
    units = int(cleaned["Quantity"].sum())
    avg_order_value = total_sales / total_orders if total_orders else 0
    best_product = str(product_summary.iloc[0]["Product"]) if len(product_summary) else "N/A"
    best_region = str(region_summary.iloc[0]["Region"]) if len(region_summary) else "N/A"
    summary = {
        "total_sales": round(total_sales, 2),
        "unique_orders": total_orders,
        "units_sold": units,
        "average_sales_per_order": round(avg_order_value, 2),
        "top_product_by_sales": best_product,
        "top_region_by_sales": best_region,
        **metrics
    }
    (output_dir / "executive_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Automated Sales & Data Quality Summary", "",
        f"- **Total sales:** ₹{total_sales:,.2f}",
        f"- **Unique orders:** {total_orders:,}",
        f"- **Units sold:** {units:,}",
        f"- **Average sales per order:** ₹{avg_order_value:,.2f}",
        f"- **Top product by sales:** {best_product}",
        f"- **Top region by sales:** {best_region}",
        f"- **Rows before cleaning:** {metrics['rows_before']:,}",
        f"- **Rows after cleaning:** {metrics['rows_after']:,}",
        f"- **Exact duplicates removed:** {metrics['duplicate_rows_removed']:,}",
        f"- **Missing cells after cleaning:** {metrics['missing_cells_after_cleaning']:,}",
        "",
        "## Cleaning notes",
        "- Exact duplicate rows were removed.",
        "- Text labels were trimmed and normalized to title case.",
        "- Invalid non-positive quantities were removed because valid sales could not be inferred.",
        "- Missing prices were filled with the median price; missing discounts were set to 0.",
        "- Missing category/region/channel labels were set to `Unknown`.",
        "- Sales_Amount was recalculated from Quantity × Unit_Price × (1 − Discount).",
    ]
    (output_dir / "executive_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Charts
    plt.figure(figsize=(11, 5))
    plt.plot(monthly_summary["Month"], monthly_summary["Total_Sales"], marker="o")
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Sales (INR)")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(charts_dir / "monthly_sales_trend.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.bar(product_summary["Product"], product_summary["Total_Sales"])
    plt.title("Sales by Product")
    plt.xlabel("Product")
    plt.ylabel("Sales (INR)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(charts_dir / "sales_by_product.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(region_summary["Region"], region_summary["Total_Sales"])
    plt.title("Sales by Region")
    plt.xlabel("Region")
    plt.ylabel("Sales (INR)")
    plt.tight_layout()
    plt.savefig(charts_dir / "sales_by_region.png", dpi=150)
    plt.close()

    # Data quality snapshot
    qlabels = ["Missing cells\n(before)", "Missing cells\n(after)", "Duplicates\nremoved", "Rows removed"]
    qvals = [metrics["missing_cells_before_cleaning"], metrics["missing_cells_after_cleaning"],
             metrics["duplicate_rows_removed"], metrics["rows_removed_total"]]
    plt.figure(figsize=(8, 5))
    plt.bar(qlabels, qvals)
    plt.title("Data Quality: Before vs After Cleaning")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(charts_dir / "data_quality_overview.png", dpi=150)
    plt.close()

    return cleaned, metrics, summary

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    cleaned, metrics, summary = build_reports(root / "data" / "raw_sales_data.csv", root / "reports")
    print("Project run completed.")
    print(f"Cleaned data: {root / 'data' / 'cleaned_sales_data.csv'}")
    print(f"Reports: {root / 'reports'}")
    print(f"Rows: {metrics['rows_before']} -> {metrics['rows_after']}")
    print(f"Total sales: ₹{summary['total_sales']:,.2f}")
