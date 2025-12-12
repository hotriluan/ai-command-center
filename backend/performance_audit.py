
import requests
import time
import statistics
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:@localhost/ai_command_center"
API_URL = "http://localhost:8000/api/dashboard?year=2024"

def audit_database():
    engine = create_engine(DATABASE_URL)
    print("=== DATABASE STRUCTURE AUDIT ===")
    with engine.connect() as conn:
        # Table Create Statement
        print("\n[1] SHOW CREATE TABLE sales_data:")
        try:
            result = conn.execute(text("SHOW CREATE TABLE sales_data")).fetchone()
            print(result[1])
        except Exception as e:
            print(f"Error: {e}")

        # Indexes
        print("\n[2] SHOW INDEX FROM sales_data:")
        try:
            indexes = conn.execute(text("SHOW INDEX FROM sales_data")).fetchall()
            print(f"{'Key_name':<25} {'Column_name':<20} {'Seq_in_index'}")
            print("-" * 60)
            for idx in indexes:
                # idx structure depends on driver, usually:
                # 0=Table, 1=Non_unique, 2=Key_name, 3=Seq_in_index, 4=Column_name...
                # Let's assume pymysql returns tuples matching SHOW INDEX columns roughly
                # Or easier, access by name if mapped, but result is Row.
                # Let's inspect the Row object or print raw
                print(f"{idx.Key_name:<25} {idx.Column_name:<20} {idx.Seq_in_index}")
        except Exception as e:
            print(f"Error: {e}")

        # Explain Query
        print("\n[3] EXPLAIN QUERY (Dashboard Stats):")
        query = "SELECT * FROM view_sales_performance_v2 WHERE year = 2024"
        try:
            explain = conn.execute(text(f"EXPLAIN {query}")).fetchall()
            print(f"{'id':<5} {'select_type':<15} {'table':<20} {'type':<10} {'key':<20} {'rows':<10} {'Extra'}")
            print("-" * 100)
            for row in explain:
                 print(f"{row.id:<5} {row.select_type:<15} {str(row.table):<20} {row.type:<10} {str(row.key):<20} {str(row.rows):<10} {row.Extra}")
        except Exception as e:
            print(f"Error: {e}")

def measure_latency():
    print("\n=== LATENCY TEST ===")
    latencies = []
    print(f"Target: {API_URL}")
    
    # Warmup
    try:
        requests.get(API_URL)
    except:
        pass

    for i in range(1, 11):
        start = time.time()
        try:
            resp = requests.get(API_URL)
            if resp.status_code == 200:
                elapsed = (time.time() - start) * 1000 # ms
                latencies.append(elapsed)
                print(f"Request {i}: {elapsed:.2f} ms")
            else:
                print(f"Request {i}: Failed ({resp.status_code})")
        except Exception as e:
             print(f"Request {i}: Error {e}")
    
    if latencies:
        avg = statistics.mean(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 2 else latencies[-1] # Simple approx
        print(f"\nAverage Latency: {avg:.2f} ms")
        print(f"Max Latency: {max(latencies):.2f} ms")
        print(f"Min Latency: {min(latencies):.2f} ms")

if __name__ == "__main__":
    audit_database()
    measure_latency()
