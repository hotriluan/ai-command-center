
import sys
import time
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:@localhost/ai_command_center"

# Query counter
query_count = 0
queries_executed = []

def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    global query_count, queries_executed
    query_count += 1
    queries_executed.append({
        'num': query_count,
        'sql': statement[:150] + '...' if len(statement) > 150 else statement
    })

print("=" * 80)
print("FORENSIC PERFORMANCE AUDIT")
print("=" * 80)

# CHECK 1: Verify Schema & Indexes
print("\n[CHECK 1] Schema & Index Verification")
print("-" * 80)

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Show CREATE TABLE
    result = conn.execute(text("SHOW CREATE TABLE sales_data"))
    create_stmt = result.fetchone()[1]
    
    print("\nCREATE TABLE Statement:")
    print(create_stmt)
    
    # Parse for critical columns
    print("\n[ANALYSIS]")
    if "dist` varchar" in create_stmt.lower():
        print("  [OK] Column 'dist' is VARCHAR")
    elif "dist` text" in create_stmt.lower():
        print("  [FAIL] Column 'dist' is still TEXT")
    
    if "salesman_name` varchar" in create_stmt.lower():
        print("  [OK] Column 'salesman_name' is VARCHAR")
    elif "salesman_name` text" in create_stmt.lower():
        print("  [FAIL] Column 'salesman_name' is still TEXT")
    
    # Check indexes
    print("\n[INDEXES]")
    result = conn.execute(text("SHOW INDEX FROM sales_data"))
    indexes = result.fetchall()
    index_names = set([idx.Key_name for idx in indexes])
    
    for idx_name in ['idx_sales_year', 'idx_sales_dist', 'idx_sales_salesman', 'idx_sales_desc']:
        if idx_name in index_names:
            print(f"  [OK] Index '{idx_name}' exists")
        else:
            print(f"  [MISSING] Index '{idx_name}'")

# CHECK 2: N+1 Query Detection
print("\n" + "=" * 80)
print("[CHECK 2] N+1 Query Detection")
print("-" * 80)

# Reset counter
query_count = 0
queries_executed = []

# Create engine with event listener
engine_with_logging = create_engine(DATABASE_URL)
event.listen(engine_with_logging, "before_cursor_execute", before_cursor_execute)

SessionLocal = sessionmaker(bind=engine_with_logging)
db = SessionLocal()

print("\nCalling year_services.get_dashboard_stats_by_year(db, 2024)...")

start_time = time.time()
try:
    import year_services
    result = year_services.get_dashboard_stats_by_year(db, 2024)
    elapsed = time.time() - start_time
    
    print(f"\n[RESULTS]")
    print(f"  Total Queries Executed: {query_count}")
    print(f"  Execution Time: {elapsed:.3f}s ({elapsed*1000:.0f}ms)")
    
    if query_count <= 5:
        print(f"  [OK] Query count is acceptable (<= 5)")
    elif query_count <= 15:
        print(f"  [WARNING] Query count is moderate (6-15)")
    else:
        print(f"  [CRITICAL] N+1 Query Problem! ({query_count} queries)")
        print(f"\n  First 10 queries:")
        for q in queries_executed[:10]:
            print(f"    [{q['num']}] {q['sql']}")
    
except Exception as e:
    print(f"  [ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

# CHECK 3: Raw Latency Benchmark
print("\n" + "=" * 80)
print("[CHECK 3] Raw Latency Benchmark")
print("-" * 80)

engine_clean = create_engine(DATABASE_URL)

# Test 1: Simple SELECT 1
with engine_clean.connect() as conn:
    start = time.time()
    conn.execute(text("SELECT 1"))
    ping_time = (time.time() - start) * 1000
    print(f"\nMySQL Ping (SELECT 1): {ping_time:.2f}ms")

# Test 2: Count sales_data
with engine_clean.connect() as conn:
    start = time.time()
    result = conn.execute(text("SELECT COUNT(*) FROM sales_data WHERE year = 2024"))
    count_time = (time.time() - start) * 1000
    count = result.scalar()
    print(f"Count Query (year=2024): {count_time:.2f}ms ({count:,} rows)")

# Test 3: View query
with engine_clean.connect() as conn:
    start = time.time()
    result = conn.execute(text("SELECT COUNT(*) FROM view_sales_performance_v2 WHERE year = 2024"))
    view_time = (time.time() - start) * 1000
    view_count = result.scalar()
    print(f"View Query (year=2024): {view_time:.2f}ms ({view_count:,} rows)")

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
