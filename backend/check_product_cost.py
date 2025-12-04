from database import engine
from sqlalchemy import text

def check_product_cost():
    print("Checking ProductCost table...")
    with engine.connect() as conn:
        # Check if table exists
        res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='product_cost'"))
        if not res.fetchone():
            print("❌ product_cost table MISSING")
            return

        result = conn.execute(text("PRAGMA table_info(product_cost)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"Columns in product_cost: {columns}")
        
        if 'cogs' in columns:
            print("✅ cogs column EXISTS")
        else:
            print("❌ cogs column MISSING")

if __name__ == "__main__":
    check_product_cost()
