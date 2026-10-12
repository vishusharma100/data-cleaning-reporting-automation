# Automated Sales & Data Quality Summary

- **Total sales:** ₹35,369,758.24
- **Unique orders:** 645
- **Units sold:** 1,929
- **Average sales per order:** ₹54,836.83
- **Top product by sales:** Laptop
- **Top region by sales:** South
- **Rows before cleaning:** 664
- **Rows after cleaning:** 645
- **Exact duplicates removed:** 14
- **Missing cells after cleaning:** 0

## Cleaning notes
- Exact duplicate rows were removed.
- Text labels were trimmed and normalized to title case.
- Invalid non-positive quantities were removed because valid sales could not be inferred.
- Missing prices were filled with the median price; missing discounts were set to 0.
- Missing category/region/channel labels were set to `Unknown`.
- Sales_Amount was recalculated from Quantity × Unit_Price × (1 − Discount).
