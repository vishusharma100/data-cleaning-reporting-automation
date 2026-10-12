"""One-command runner for cleaning and reporting."""
from pathlib import Path
import sys
from generate_report import build_reports

def main():
    root = Path(__file__).resolve().parents[1]
    raw_path = root / "data" / "raw_sales_data.csv"
    report_dir = root / "reports"
    _, metrics, summary = build_reports(raw_path, report_dir)
    print("\n=== DATA CLEANING & REPORTING AUTOMATION ===")
    print(f"Rows: {metrics['rows_before']} -> {metrics['rows_after']}")
    print(f"Duplicate rows removed: {metrics['duplicate_rows_removed']}")
    print(f"Missing cells after cleaning: {metrics['missing_cells_after_cleaning']}")
    print(f"Total sales: ₹{summary['total_sales']:,.2f}")
    print(f"Top product: {summary['top_product_by_sales']}")
    print(f"Top region: {summary['top_region_by_sales']}")
    print("\nReports and charts saved in the reports/ folder.")

if __name__ == "__main__":
    main()
