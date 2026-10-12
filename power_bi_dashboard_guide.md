# Power BI Dashboard Guide

## Before you start
Run `python src/main.py` from the project root so `data/cleaned_sales_data.csv` exists.

## Import
Power BI Desktop → Home → Get data → Text/CSV → select `data/cleaned_sales_data.csv` → Load.

## Data types
- Order_Date: Date
- Quantity: Whole number
- Unit_Price, Discount, Sales_Amount: Decimal number
- Order_ID, Customer_ID, Product, Category, Region, Sales_Channel: Text

## Measures (Modeling → New measure)
```DAX
Total Sales = SUM(cleaned_sales_data[Sales_Amount])
Total Orders = DISTINCTCOUNT(cleaned_sales_data[Order_ID])
Units Sold = SUM(cleaned_sales_data[Quantity])
Average Order Value = DIVIDE([Total Sales], [Total Orders])
Average Discount = AVERAGE(cleaned_sales_data[Discount])
```

## Suggested layout
Top row: KPI cards for Total Sales, Total Orders, Units Sold, Average Order Value.
Middle row: Monthly Sales Trend (line chart) and Sales by Product (bar chart).
Bottom row: Sales by Region (column chart) and Sales by Channel (donut chart).
Add slicers for Order_Date, Region, Product, and Sales_Channel.

## Save
Save as `dashboard/sales_reporting_dashboard.pbix`. Power BI Desktop is required to create the actual PBIX file.
