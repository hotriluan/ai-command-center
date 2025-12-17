"""Quick performance verification after backend restart"""
from database import SessionLocal
from sqlalchemy import text
import time

db = SessionLocal()

print("\n" + "=" * 60)
print("QUICK PERFORMANCE VERIFICATION")
print("=" * 60)

# Test 1: Dashboard KPI Query
print("\n[Test 1] Dashboard KPI Query...")
start = time.time()
result = db.execute(text("""
    SELECT SUM(net_value), SUM(profit) 
    FROM sales_data 
    WHERE year = 2024
""")).fetchone()
elapsed = time.time() - start

print(f"  Time: {elapsed:.3f}s")
print(f"  Revenue: {result[0]:,.0f} VND")
print(f"  Profit: {result[1]:,.0f} VND")
print(f"  Status: {'✅ FAST' if elapsed < 1.0 else '⚠️ SLOW'}")

# Test 2: Monthly Trend
print("\n[Test 2] Monthly Trend Query...")
start = time.time()
result = db.execute(text("""
    SELECT month_number, SUM(net_value) 
    FROM sales_data 
    WHERE year = 2024 
    GROUP BY month_number 
    ORDER BY month_number
""")).fetchall()
elapsed = time.time() - start

print(f"  Time: {elapsed:.3f}s")
print(f"  Months: {len(result)}")
print(f"  Status: {'✅ FAST' if elapsed < 0.5 else '⚠️ SLOW'}")

# Test 3: Check if indexes are being used
print("\n[Test 3] Index Usage Check...")
result = db.execute(text("""
    EXPLAIN SELECT * FROM sales_data 
    WHERE year = 2024 AND month_number = 10
""")).fetchone()

print(f"  Access type: {result[3]}")
print(f"  Key used: {result[5] or 'NONE - Full table scan!'}")
print(f"  Rows scanned: {result[8]}")
print(f"  Status: {'✅ Using index' if result[5] else '❌ No index used'}")

db.close()

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE")
print("=" * 60)
