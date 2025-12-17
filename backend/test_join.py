from database import engine
import pandas as pd

query = """
SELECT p.order_id, p.order_type, p.sales_order_id, s.billing_document, s.billing_date
FROM production_orders p
LEFT JOIN sales_data s ON CONVERT(p.sales_order_id, CHAR) = CONVERT(s.billing_document, CHAR)
WHERE p.actual_finish_date IS NOT NULL 
  AND p.order_type = '201O'
LIMIT 10
"""

df = pd.read_sql(query, engine)
print(df)
print(f"\nJOIN Success: {df['billing_document'].notna().sum()} matches out of {len(df)}")
