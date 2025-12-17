"""
Drop and recreate sales_data table with correct schema
"""
from database import engine
from sqlalchemy import text

def recreate_sales_data_table():
    connection = engine.raw_connection()
    cursor = connection.cursor()
    
    try:
        print("\n" + "=" * 80)
        print("RECREATING SALES_DATA TABLE")
        print("=" * 80)
        
        # Step 1: Drop existing table
        print("\n[STEP 1] Dropping existing sales_data table...")
        cursor.execute("DROP TABLE IF EXISTS sales_data")
        connection.commit()
        print("  ✅ Table dropped")
        
        # Step 2: Create new table with correct schema
        print("\n[STEP 2] Creating new sales_data table with correct schema...")
        
        create_table_sql = """
        CREATE TABLE sales_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            
            -- Transaction identifiers
            billing_document VARCHAR(100),
            billing_item VARCHAR(100),
            material_code VARCHAR(100),
            so_no VARCHAR(100),
            
            -- Dates
            billing_date VARCHAR(20),
            so_date VARCHAR(20),
            
            -- Time dimensions
            year INT,
            month VARCHAR(20),
            month_number INT,
            
            -- Organizational dimensions
            dist VARCHAR(100),
            branch VARCHAR(100),
            salesman_name VARCHAR(255),
            
            -- Product dimensions
            product_group VARCHAR(100),
            description VARCHAR(500),
            
            -- Customer
            customer_name VARCHAR(255),
            
            -- Metrics
            billing_qty FLOAT,
            net_value FLOAT,
            profit FLOAT DEFAULT 0,
            marketing_spend FLOAT DEFAULT 0,
            
            -- Indexes for performance
            INDEX idx_billing_doc (billing_document),
            INDEX idx_material (material_code),
            INDEX idx_so_no (so_no),
            INDEX idx_year (year),
            INDEX idx_dist (dist),
            INDEX idx_salesman (salesman_name),
            INDEX idx_customer (customer_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        print("  ✅ Table created successfully")
        
        # Step 3: Verify schema
        print("\n[STEP 3] Verifying new schema...")
        cursor.execute("SHOW COLUMNS FROM sales_data")
        print("\n  Columns:")
        for row in cursor.fetchall():
            key_info = f" [{row[3]}]" if row[3] else ""
            print(f"    - {row[0]:20} {row[1]:20}{key_info}")
        
        # Check indexes
        cursor.execute("SHOW INDEX FROM sales_data")
        print("\n  Indexes:")
        indexes = {}
        for row in cursor.fetchall():
            idx_name = row[2]
            col_name = row[4]
            if idx_name not in indexes:
                indexes[idx_name] = []
            indexes[idx_name].append(col_name)
        
        for idx_name, cols in indexes.items():
            print(f"    - {idx_name}: {', '.join(cols)}")
        
        print("\n" + "=" * 80)
        print("✅ TABLE RECREATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nThe sales_data table is now ready for imports!")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        cursor.close()
        connection.close()
        return False

if __name__ == "__main__":
    success = recreate_sales_data_table()
    exit(0 if success else 1)
