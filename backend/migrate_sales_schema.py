"""
Database Migration Script for sales_data table
Purpose: Update schema to match SalesData model definition
"""
from database import engine
from sqlalchemy import text

def migrate_sales_data_schema():
    """
    Migrate sales_data table schema to match the SalesData model
    - Rename existing columns
    - Add missing columns
    """
    print("\n" + "=" * 80)
    print("SALES DATA SCHEMA MIGRATION")
    print("=" * 80)
    
    # Use raw connection with autocommit
    connection = engine.raw_connection()
    
    try:
        cursor = connection.cursor()
        
        print("\n[STEP 1] Renaming existing columns...")
        
        # Rename columns to match model
        # Format: (old_name, new_name, data_type)
        rename_operations = [
            ("month_num", "month_number", "INTEGER"),
            ("month_label", "month", "VARCHAR(20)"),
            ("dist_channel", "dist", "VARCHAR(100)"),
            ("product_desc", "description", "VARCHAR(500)"),
            ("revenue", "net_value", "FLOAT")
        ]
        
        for old_name, new_name, data_type in rename_operations:
            try:
                sql = f"ALTER TABLE sales_data CHANGE COLUMN `{old_name}` `{new_name}` {data_type}"
                cursor.execute(sql)
                connection.commit()
                print(f"  ✅ Renamed: {old_name} → {new_name} ({data_type})")
            except Exception as e:
                error_msg = str(e).lower()
                if "doesn't exist" in error_msg or "unknown column" in error_msg:
                    print(f"  ⏭️  Column {old_name} already renamed or doesn't exist")
                else:
                    print(f"  ❌ Error renaming {old_name}: {e}")
                    raise
        
        print("\n[STEP 2] Adding missing columns...")
        
        # Add new columns required by the model
        new_columns = [
            ("profit", "FLOAT DEFAULT 0"),
            ("marketing_spend", "FLOAT DEFAULT 0"),
            ("billing_document", "VARCHAR(100)"),
            ("billing_item", "VARCHAR(100)"),
            ("material_code", "VARCHAR(100)"),
            ("billing_date", "VARCHAR(20)"),
            ("so_no", "VARCHAR(100)"),
            ("so_date", "VARCHAR(20)")
        ]
        
        for col_name, col_type in new_columns:
            try:
                sql = f"ALTER TABLE sales_data ADD COLUMN `{col_name}` {col_type}"
                cursor.execute(sql)
                connection.commit()
                print(f"  ✅ Added: {col_name} ({col_type})")
            except Exception as e:
                error_msg = str(e).lower()
                if "duplicate column" in error_msg:
                    print(f"  ⏭️  Column {col_name} already exists")
                else:
                    print(f"  ❌ Error adding {col_name}: {e}")
                    raise
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        # Verify the new schema
        print("\n[VERIFICATION] Current schema:")
        cursor.execute("DESCRIBE sales_data")
        for row in cursor.fetchall():
            print(f"  - {row[0]} ({row[1]})")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        connection.close()
        return False


if __name__ == "__main__":
    success = migrate_sales_data_schema()
    exit(0 if success else 1)
