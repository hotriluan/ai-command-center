"""
Direct SQL migration for sales_data table
"""
from database import engine

def run_migration():
    connection = engine.raw_connection()
    cursor = connection.cursor()
    
    try:
        # First, let's see what we have
        print("Current schema:")
        cursor.execute("SHOW COLUMNS FROM sales_data")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        print("\n" + "=" * 80)
        print("Starting migration...")
        print("=" * 80)
        
        # Rename columns one by one
        migrations = [
            "ALTER TABLE sales_data CHANGE COLUMN `month_num` `month_number` INT",
            "ALTER TABLE sales_data CHANGE COLUMN `month_label` `month` VARCHAR(20)",
            "ALTER TABLE sales_data CHANGE COLUMN `dist_channel` `dist` VARCHAR(100)",
            "ALTER TABLE sales_data CHANGE COLUMN `product_desc` `description` VARCHAR(500)",
            "ALTER TABLE sales_data CHANGE COLUMN `revenue` `net_value` FLOAT",
        ]
        
        for sql in migrations:
            try:
                print(f"\nExecuting: {sql}")
                cursor.execute(sql)
                connection.commit()
                print("  ✅ Success")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                if "unknown column" not in str(e).lower():
                    raise
        
        # Add new columns
        new_columns = [
            "ALTER TABLE sales_data ADD COLUMN `profit` FLOAT DEFAULT 0",
            "ALTER TABLE sales_data ADD COLUMN `marketing_spend` FLOAT DEFAULT 0",
            "ALTER TABLE sales_data ADD COLUMN `billing_document` VARCHAR(100)",
            "ALTER TABLE sales_data ADD COLUMN `billing_item` VARCHAR(100)",
            "ALTER TABLE sales_data ADD COLUMN `material_code` VARCHAR(100)",
            "ALTER TABLE sales_data ADD COLUMN `billing_date` VARCHAR(20)",
            "ALTER TABLE sales_data ADD COLUMN `so_no` VARCHAR(100)",
            "ALTER TABLE sales_data ADD COLUMN `so_date` VARCHAR(20)",
        ]
        
        for sql in new_columns:
            try:
                print(f"\nExecuting: {sql}")
                cursor.execute(sql)
                connection.commit()
                print("  ✅ Success")
            except Exception as e:
                print(f"  ⚠️  {e}")
                if "duplicate" not in str(e).lower():
                    raise
        
        print("\n" + "=" * 80)
        print("Final schema:")
        print("=" * 80)
        cursor.execute("SHOW COLUMNS FROM sales_data")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        cursor.close()
        connection.close()
        print("\n✅ Migration completed!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        cursor.close()
        connection.close()

if __name__ == "__main__":
    run_migration()
