
from sqlalchemy import create_engine, text
import time

DATABASE_URL = "mysql+pymysql://root:@localhost/ai_command_center"
engine = create_engine(DATABASE_URL)

def optimize_schema():
    print("=== STARTING DATABASE OPTIMIZATION ===")
    
    commands = [
        # 1. Convert TEXT to VARCHAR(255) to allow indexing and in-memory sorting
        ("Converting sales_data.dist", "ALTER TABLE sales_data MODIFY dist VARCHAR(255)"),
        ("Converting sales_data.branch", "ALTER TABLE sales_data MODIFY branch VARCHAR(255)"),
        ("Converting sales_data.salesman_name", "ALTER TABLE sales_data MODIFY salesman_name VARCHAR(255)"),
        ("Converting sales_data.description", "ALTER TABLE sales_data MODIFY description VARCHAR(255)"),
        ("Converting sales_data.material_code", "ALTER TABLE sales_data MODIFY material_code VARCHAR(100)"),
        ("Converting sales_data.product_group", "ALTER TABLE sales_data MODIFY product_group VARCHAR(100)"),
        
        ("Converting product_cost.description", "ALTER TABLE product_cost MODIFY description VARCHAR(255)"),
        
        # 2. Add Missing Indexes
        ("Indexing sales_data.dist", "CREATE INDEX idx_sales_dist ON sales_data(dist)"),
        ("Indexing sales_data.salesman_name", "CREATE INDEX idx_sales_salesman ON sales_data(salesman_name)"),
        ("Indexing sales_data.description", "CREATE INDEX idx_sales_desc ON sales_data(description)"),
        
        ("Indexing product_cost.description", "CREATE INDEX idx_cost_desc ON product_cost(description)")
    ]
    
    with engine.connect() as conn:
        for desc, sql in commands:
            print(f"\n[Running] {desc}...")
            start = time.time()
            try:
                # Check for duplicate indexes to avoid errors
                if "CREATE INDEX" in sql:
                    idx_name = sql.split()[2]
                    table_name = sql.split()[4].split('(')[0]
                    check_sql = text(f"SHOW INDEX FROM {table_name} WHERE Key_name = '{idx_name}'")
                    if conn.execute(check_sql).fetchone():
                        print(f"  ⚠ Index {idx_name} already exists. Skipped.")
                        continue
                
                conn.execute(text(sql))
                conn.commit()
                print(f"  ✓ Done ({time.time() - start:.2f}s)")
            except Exception as e:
                print(f"  ✗ Failed: {e}")

    print("\n=== OPTIMIZATION COMPLETE ===")

if __name__ == "__main__":
    optimize_schema()
