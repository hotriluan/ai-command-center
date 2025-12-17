"""
Database Migration: Add Sales Order columns to sales_data table
Date: 2025-12-16
Purpose: Enable MTO timeline tracking by linking production orders to sales orders
"""

from database import SessionLocal
from sqlalchemy import text

def migrate_add_so_columns():
    """
    Add so_no and so_date columns to sales_data table
    Also add missing columns to production_orders table
    """
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("DATABASE MIGRATION: Add Sales Order Columns")
        print("=" * 80)
        
        # Step 1: Add columns to sales_data
        print("\n[Step 1] Adding columns to sales_data table...")
        
        try:
            db.execute(text("""
                ALTER TABLE sales_data 
                ADD COLUMN so_no VARCHAR(50)
            """))
            print("  ✅ Added column: so_no")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("  ⚠️  Column so_no already exists, skipping...")
            else:
                raise
        
        try:
            db.execute(text("""
                ALTER TABLE sales_data 
                ADD COLUMN so_date DATE
            """))
            print("  ✅ Added column: so_date")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("  ⚠️  Column so_date already exists, skipping...")
            else:
                raise
        
        db.commit()
        
        # Step 2: Create index for performance
        print("\n[Step 2] Creating index on so_no...")
        
        try:
            db.execute(text("""
                CREATE INDEX idx_sales_data_so_no ON sales_data(so_no)
            """))
            print("  ✅ Created index: idx_sales_data_so_no")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("  ⚠️  Index already exists, skipping...")
            else:
                raise
        
        db.commit()
        
        # Step 3: Add missing columns to production_orders
        print("\n[Step 3] Adding missing columns to production_orders table...")
        
        missing_columns = [
            ("basic_start_date", "DATE"),
            ("bom_alternative", "VARCHAR(20)"),
            ("system_status", "VARCHAR(100)")
        ]
        
        for col_name, col_type in missing_columns:
            try:
                db.execute(text(f"""
                    ALTER TABLE production_orders 
                    ADD COLUMN {col_name} {col_type}
                """))
                print(f"  ✅ Added column: {col_name}")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"  ⚠️  Column {col_name} already exists, skipping...")
                else:
                    raise
        
        db.commit()
        
        # Step 4: Verify changes
        print("\n[Step 4] Verifying changes...")
        
        # Check sales_data columns
        result = db.execute(text("SHOW COLUMNS FROM sales_data"))
        sales_cols = [row[0] for row in result.fetchall()]
        
        if 'so_no' in sales_cols and 'so_date' in sales_cols:
            print("  ✅ sales_data: so_no and so_date columns verified")
        else:
            print("  ❌ sales_data: Missing columns!")
        
        # Check production_orders columns
        result = db.execute(text("SHOW COLUMNS FROM production_orders"))
        prod_cols = [row[0] for row in result.fetchall()]
        
        missing_found = all(col in prod_cols for col, _ in missing_columns)
        if missing_found:
            print("  ✅ production_orders: All new columns verified")
        else:
            print("  ❌ production_orders: Missing columns!")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Update import_sales_data() to extract SO No. and SO Date")
        print("2. Update import_production_data() to extract new columns")
        print("3. Re-import data to populate new columns")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_so_columns()
