from database import get_db
import pandas as pd
from sqlalchemy import text

db = next(get_db())

query = """
    SELECT 
        p.order_id,
        p.plant,
        p.order_type,
        p.material_code,
        p.material_description,
        p.sales_order_id,
        p.release_date,
        p.actual_finish_date,
        p.batch,
        p.mrp_controller,
        p.order_qty,
        p.delivered_qty,
        p.unit,
        s.billing_date as so_billing_date,
        s.billing_document as so_number
    FROM production_orders p
    LEFT JOIN sales_data s ON CONVERT(p.sales_order_id, CHAR) = CONVERT(s.billing_document, CHAR)
    WHERE p.actual_finish_date IS NOT NULL
      AND p.release_date IS NOT NULL
      AND p.release_date >= :start_date
      AND p.release_date <= :end_date
"""

params = {'start_date': '2025-11-01', 'end_date': '2025-12-31'}

df = pd.read_sql(text(query), db.get_bind(), params=params)

print(f"Query returned {len(df)} rows")
if len(df) > 0:
    print("\nFirst 3 rows:")
    print(df.head(3))
    print("\nOrder type breakdown:")
    print(df['order_type'].value_counts())
else:
    print("\nDF is EMPTY! Checking why...")
    # Test without date filter
    query2 = "SELECT COUNT(*) as cnt FROM production_orders WHERE actual_finish_date IS NOT NULL AND release_date IS NOT NULL"
    result = pd.read_sql(query2, db.get_bind())
    print(f"Total rows without date filter: {result['cnt'][0]}")
    
    # Check date range
    query3 = "SELECT MIN(release_date) as min_date, MAX(release_date) as max_date FROM production_orders WHERE release_date IS NOT NULL"
    dates = pd.read_sql(query3, db.get_bind())
    print(f"Release date range: {dates['min_date'][0]} to {dates['max_date'][0]}")
