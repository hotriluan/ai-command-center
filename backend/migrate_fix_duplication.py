"""
Migration Script: Fix Data Duplication Issue
Adds missing columns and creates unique index
"""
import sqlite3
import os

def migrate_fix_duplication():
    """Add missing columns and create unique index"""
    db_path = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
    
    print("=" * 80)
    print("MIGRATION: Fix Data Duplication")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # STEP 1: Add Missing Columns
        print("\n[STEP 1] Adding missing columns to sales_data...")
        
        columns_to_add = [
            ('billing_document', 'TEXT'),
            ('billing_item', 'TEXT'),
            ('material_code', 'TEXT'),
            ('billing_date', 'TEXT')
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE sales_data ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added column: {col_name} ({col_type})")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ⚠️ Column {col_name} already exists, skipping")
                else:
                    raise
        
        conn.commit()
        
        # STEP 2: Verify columns
        print("\n[STEP 2] Verifying schema...")
        cursor.execute("PRAGMA table_info(sales_data)")
        columns = cursor.fetchall()
        
        col_names = [col[1] for col in columns]
        print(f"  Total columns: {len(col_names)}")
        
        required = ['billing_document', 'billing_item', 'material_code', 'billing_date']
        for req in required:
            status = "✅" if req in col_names else "❌"
            print(f"  {status} {req}")
        
        # STEP 3: Create Unique Index
        print("\n[STEP 3] Creating unique index...")
        
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_sales_transaction 
                ON sales_data (billing_document, billing_item)
            """)
            print("  ✅ Created unique index: idx_unique_sales_transaction")
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️ Cannot create unique index: {e}")
            print(f"  Reason: Existing NULL values or duplicates")
            print(f"  Note: Index will be created after cleanup")
        
        conn.commit()
        
        # STEP 4: Verify index
        print("\n[STEP 4] Verifying indices...")
        cursor.execute("PRAGMA index_list('sales_data')")
        indices = cursor.fetchall()
        
        if indices:
            for idx in indices:
                idx_name = idx[1]
                is_unique = "UNIQUE" if idx[2] == 1 else "NON-UNIQUE"
                print(f"  ✅ {idx_name}: {is_unique}")
        else:
            print("  ⚠️ No indices found (will be created after cleanup)")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED")
        print("=" * 80)
        print("\nNOTE: If unique index creation failed, run cleanup script first.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_fix_duplication()
