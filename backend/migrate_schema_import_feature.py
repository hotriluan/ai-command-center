"""
Schema Migration Script for Data Import Feature
Purpose: Safely extend sales_data table and create product_cogs table
CRITICAL: Does NOT drop existing tables or delete data
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')

def run_migration():
    """Execute schema migration safely"""
    print("=" * 80)
    print("SCHEMA MIGRATION: Data Import & Upsert Feature")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now()}\n")
    
    # Backup reminder
    print("⚠️  IMPORTANT: Ensure you have a backup of command_center_v2.db before proceeding!")
    print("   Press Ctrl+C to cancel, or wait 3 seconds to continue...\n")
    
    import time
    time.sleep(3)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Step 1: Extend sales_data table
        print("\n[Step 1] Extending sales_data table...")
        
        columns_to_add = [
            ("billing_document", "TEXT"),
            ("billing_item", "TEXT"),
            ("material_code", "TEXT"),
            ("billing_date", "TEXT")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE sales_data ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added column: {col_name} ({col_type})")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  ⏭️  Column already exists: {col_name}")
                else:
                    raise
        
        # Step 2: Create product_cogs table
        print("\n[Step 2] Creating product_cogs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_cogs (
                material_code TEXT PRIMARY KEY,
                description TEXT,
                cogs_price REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Table created/verified: product_cogs")
        
        # Step 3: Create unique index on sales_data
        print("\n[Step 3] Creating unique index on sales_data...")
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_sales_unique_transaction 
            ON sales_data (billing_document, billing_item)
        """)
        print("  ✅ Unique index created: idx_sales_unique_transaction")
        
        # Commit all changes
        conn.commit()
        
        # Verification
        print("\n[Verification] Checking schema...")
        cursor.execute("PRAGMA table_info(sales_data)")
        sales_cols = [row[1] for row in cursor.fetchall()]
        print(f"  sales_data columns: {len(sales_cols)}")
        for col in ["billing_document", "billing_item", "material_code", "billing_date"]:
            status = "✅" if col in sales_cols else "❌"
            print(f"    {status} {col}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_cogs'")
        if cursor.fetchone():
            print("  ✅ product_cogs table exists")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_sales_unique_transaction'")
        if cursor.fetchone():
            print("  ✅ idx_sales_unique_transaction index exists")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
