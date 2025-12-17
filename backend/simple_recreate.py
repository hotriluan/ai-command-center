"""
Simple script to drop and recreate sales_data table
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Get database credentials
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ai_command_center'),
    'charset': 'utf8mb4'
}

print("\n" + "=" * 80)
print("RECREATING SALES_DATA TABLE")
print("=" * 80)

try:
    # Connect to database
    print("\n[STEP 1] Connecting to database...")
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    print("  ✅ Connected")
    
    # Drop table
    print("\n[STEP 2] Dropping existing sales_data table...")
    cursor.execute("DROP TABLE IF EXISTS sales_data")
    connection.commit()
    print("  ✅ Table dropped")
    
    # Create new table
    print("\n[STEP 3] Creating new sales_data table...")
    
    create_sql = """
    CREATE TABLE sales_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        billing_document VARCHAR(100),
        billing_item VARCHAR(100),
        material_code VARCHAR(100),
        so_no VARCHAR(100),
        billing_date VARCHAR(20),
        so_date VARCHAR(20),
        year INT,
        month VARCHAR(20),
        month_number INT,
        dist VARCHAR(100),
        branch VARCHAR(100),
        salesman_name VARCHAR(255),
        product_group VARCHAR(100),
        description VARCHAR(500),
        customer_name VARCHAR(255),
        billing_qty FLOAT,
        net_value FLOAT,
        profit FLOAT DEFAULT 0,
        marketing_spend FLOAT DEFAULT 0,
        INDEX idx_billing_doc (billing_document),
        INDEX idx_material (material_code),
        INDEX idx_so_no (so_no),
        INDEX idx_year (year),
        INDEX idx_dist (dist),
        INDEX idx_salesman (salesman_name),
        INDEX idx_customer (customer_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    cursor.execute(create_sql)
    connection.commit()
    print("  ✅ Table created")
    
    # Verify
    print("\n[STEP 4] Verifying schema...")
    cursor.execute("DESCRIBE sales_data")
    rows = cursor.fetchall()
    
    print(f"\n  Total columns: {len(rows)}")
    print("\n  Column details:")
    for row in rows:
        field, type_, null, key, default, extra = row
        key_info = f" [{key}]" if key else ""
        print(f"    {field:20} {type_:20}{key_info}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 80)
    print("✅ TABLE RECREATION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nYou can now test the import!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
