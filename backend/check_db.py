from database import SessionLocal, engine
from models import SalesData
from sqlalchemy import text

def check_db():
    print("Checking database schema...")
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(sales_data)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"Columns in sales_data: {columns}")
        
        if 'billing_qty' in columns:
            print("✅ billing_qty column EXISTS")
        else:
            print("❌ billing_qty column MISSING")
            
        # Check for id column
        if 'id' in columns:
            print("✅ id column EXISTS")
        else:
            print("❌ id column MISSING")
            
        # Count rows
        result = conn.execute(text("SELECT COUNT(*) FROM sales_data"))
        count = result.fetchone()[0]
        print(f"Total rows in sales_data: {count}")

if __name__ == "__main__":
    check_db()
