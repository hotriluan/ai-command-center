import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from analytics_services import get_target_waterfall
from year_services import get_default_year

from database import engine, SessionLocal

def debug_waterfall():
    print(f"--- DEBUG: Database URL: {engine.url} ---")
    db = SessionLocal()
    try:
        # 0. List all tables
        print("\n--- TEST 0: List all tables ---")
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' OR type='view'")).fetchall()
        for t in tables:
            print(f" - {t[0]}")

        # 1. Get Default Year
        year = get_default_year(db)
        print(f"--- DEBUG: Testing for Year: {year} ---")

        # 2. Run the function
        print("\n--- TEST 1: Calling get_target_waterfall ---")
        result = get_target_waterfall(db, year)
        print(f"Result Count: {len(result)}")
        if result:
            print(f"First Result: {result[0]}")
        else:
            print("Result is EMPTY")

        # 3. Check View Content (Concise)
        print("\n--- TEST 2: Check View Targets ---")
        query = text("""
            SELECT salesman_name, total_target 
            FROM view_sales_performance_v2 
            WHERE total_target > 0 
            LIMIT 5
        """)
        rows = db.execute(query).fetchall()
        print(f"Rows with Target > 0: {len(rows)}")
        print(f"Sample: {rows}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_waterfall()
