import sys
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from data_cleaning import clean_sales_data, load_data

class TestDataCleaning(unittest.TestCase):
    def test_cleaning_removes_duplicates_and_invalid_quantity(self):
        df = pd.DataFrame({
            "Order_ID": ["A", "A", "B"],
            "Order_Date": ["2025-01-01", "2025-01-01", "2025-01-02"],
            "Customer_ID": ["C1", "C1", "C2"],
            "Product": [" phone ", " phone ", "Laptop"],
            "Category": [" electronics ", " electronics ", "Electronics"],
            "Region": ["north", "north", "South"],
            "Sales_Channel": ["online", "online", "Retail"],
            "Quantity": [2, 2, -1],
            "Unit_Price": [100, 100, 200],
            "Discount": [0.1, 0.1, 0],
            "Sales_Amount": [180, 180, -200],
        })
        cleaned, metrics = clean_sales_data(df)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(metrics["duplicate_rows_removed"], 1)
        self.assertEqual(cleaned.iloc[0]["Product"], "Phone")
        self.assertAlmostEqual(cleaned.iloc[0]["Sales_Amount"], 180.0)

if __name__ == "__main__":
    unittest.main()
