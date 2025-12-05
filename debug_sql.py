"""
Debug SQL query for Channel Analysis
Test the exact SQL being used to see what's wrong
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 70)
print("TESTING CHANNEL ANALYSIS SQL QUERY")
print("=" * 70)

# Test 1: Check if sales_data has data
print("\n--- TEST 1: Total rows in sales_data ---")
result = db.execute(text("SELECT COUNT(*) FROM sales_data"))
total = result.fetchone()[0]
print(f"Total rows: {total:,}")

# Test 2: Check if product_cost has data
print("\n--- TEST 2: Total rows in product_cost ---")
result = db.execute(text("SELECT COUNT(*) FROM product_cost"))
total_cost = result.fetchone()[0]
print(f"Total rows: {total_cost:,}")

# Test 3: Test the EXACT SQL from the new implementation
print("\n--- TEST 3: Testing NEW SQL Query (year=2024, no semester) ---")
year = 2024
semester_condition = "1=1"

sql = text(f"""
SELECT 
    CASE 
        WHEN CAST(s.dist AS TEXT) LIKE '%11%' THEN 'Industry'
        WHEN CAST(s.dist AS TEXT) LIKE '%13%' THEN 'Retail'
        WHEN CAST(s.dist AS TEXT) LIKE '%15%' THEN 'Project'
        ELSE 'Others' 
    END as channel_name,
    
    SUM(s.net_value) as revenue,
    
    -- Profit = Revenue - (Qty * COGS)
    SUM(s.net_value - (s.billing_qty * COALESCE(pc.cogs, 0))) as profit,
    
    COUNT(*) as deals
FROM sales_data s
LEFT JOIN product_cost pc ON s.material_code = pc.material_code
WHERE (:year IS NULL OR s.year = :year)
AND {semester_condition}
GROUP BY 
    CASE 
        WHEN CAST(s.dist AS TEXT) LIKE '%11%' THEN 'Industry'
        WHEN CAST(s.dist AS TEXT) LIKE '%13%' THEN 'Retail'
        WHEN CAST(s.dist AS TEXT) LIKE '%15%' THEN 'Project'
        ELSE 'Others' 
    END
""")

try:
    result = db.execute(sql, {"year": year}).fetchall()
    print(f"Rows returned: {len(result)}")
    
    if result:
        print("\nResults:")
        for row in result:
            print(f"  Channel: {row[0]:15} Revenue: {row[1]:15,.0f} Profit: {row[2]:15,.0f} Deals: {row[3]:,}")
    else:
        print("❌ NO DATA RETURNED!")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Try simpler query without JOIN
print("\n--- TEST 4: Simple query WITHOUT product_cost JOIN ---")
simple_sql = text(f"""
SELECT 
    CASE 
        WHEN CAST(s.dist AS TEXT) LIKE '%11%' THEN 'Industry'
        WHEN CAST(s.dist AS TEXT) LIKE '%13%' THEN 'Retail'
        WHEN CAST(s.dist AS TEXT) LIKE '%15%' THEN 'Project'
        ELSE 'Others' 
    END as channel_name,
    
    SUM(s.net_value) as revenue,
    SUM(s.profit) as profit,
    COUNT(*) as deals
FROM sales_data s
WHERE s.year = :year
GROUP BY 
    CASE 
        WHEN CAST(s.dist AS TEXT) LIKE '%11%' THEN 'Industry'
        WHEN CAST(s.dist AS TEXT) LIKE '%13%' THEN 'Retail'
        WHEN CAST(s.dist AS TEXT) LIKE '%15%' THEN 'Project'
        ELSE 'Others' 
    END
""")

try:
    result = db.execute(simple_sql, {"year": year}).fetchall()
    print(f"Rows returned: {len(result)}")
    
    if result:
        print("\nResults:")
        for row in result:
            print(f"  Channel: {row[0]:15} Revenue: {row[1]:15,.0f} Profit: {row[2]:15,.0f} Deals: {row[3]:,}")
    else:
        print("❌ NO DATA RETURNED!")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check what years exist in the data
print("\n--- TEST 5: Available years in sales_data ---")
result = db.execute(text("SELECT DISTINCT year FROM sales_data ORDER BY year"))
years = [row[0] for row in result.fetchall()]
print(f"Available years: {years}")

db.close()

print("\n" + "=" * 70)
print("DEBUG COMPLETE")
print("=" * 70)
