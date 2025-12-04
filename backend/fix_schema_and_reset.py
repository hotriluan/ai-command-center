"""
Fix Schema and Reset Database
DESTRUCTIVE: Adds missing columns and purges legacy data
"""
import sqlite3
import os

def fix_schema_and_reset():
    """
    Perform schema migration and data reset
    WARNING: This will DELETE all existing sales data
    """
    db_path = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
    
    print("=" * 80)
    print("FIX SCHEMA AND RESET DATABASE")
    print("=" * 80)
    print("\n⚠️  WARNING: This will DELETE all existing sales data!")
    print("⚠️  Legacy data (77k rows) will be purged.")
    print("⚠️  You will need to re-import from Excel afterwards.\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # STEP 1: SCHEMA MIGRATION
        print("[STEP 1] Adding missing columns...")
        print("-" * 80)
        
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
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ℹ️  Column {col_name} already exists")
                else:
                    raise
        
        # STEP 2: CREATE UNIQUE INDEX
        print("\n[STEP 2] Creating unique index...")
        print("-" * 80)
        
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_sales_unique_transaction 
                ON sales_data (billing_document, billing_item)
            """)
            print("  ✅ Created unique index: idx_sales_unique_transaction")
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️  Index creation deferred: {e}")
            print("  Note: Will be enforced after data purge")
        
        # STEP 3: DATA PURGE
        print("\n[STEP 3] Purging legacy data...")
        print("-" * 80)
        
        # Count before
        cursor.execute("SELECT COUNT(*) FROM sales_data")
        before_count = cursor.fetchone()[0]
        print(f"  Records before purge: {before_count:,}")
        
        # DELETE ALL
        cursor.execute("DELETE FROM sales_data")
        deleted_count = cursor.rowcount
        
        conn.commit()
        
        print(f"  ✅ Deleted {deleted_count:,} legacy records")
        
        # STEP 4: VERIFICATION
        print("\n[STEP 4] Verification...")
        print("-" * 80)
        
        # 4a. Verify columns
        print("\n4a. Table schema:")
        cursor.execute("PRAGMA table_info(sales_data)")
        columns = cursor.fetchall()
        
        required_cols = ['billing_document', 'billing_item', 'material_code', 'billing_date']
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            is_required = col_name in required_cols
            marker = "✅" if is_required else "  "
            print(f"  {marker} {col_name:20} ({col_type})")
        
        # 4b. Verify row count
        print("\n4b. Row count:")
        cursor.execute("SELECT COUNT(*) FROM sales_data")
        after_count = cursor.fetchone()[0]
        print(f"  Total records: {after_count:,}")
        
        if after_count == 0:
            print("  ✅ Database is clean (0 records)")
        else:
            print(f"  ⚠️  Warning: {after_count} records remain")
        
        # 4c. Verify index
        print("\n4c. Indices:")
        cursor.execute("PRAGMA index_list('sales_data')")
        indices = cursor.fetchall()
        
        if indices:
            for idx in indices:
                idx_name = idx[1]
                is_unique = "UNIQUE" if idx[2] == 1 else "NON-UNIQUE"
                print(f"  ✅ {idx_name}: {is_unique}")
                
                # Show index columns
                cursor.execute(f"PRAGMA index_info('{idx_name}')")
                idx_cols = cursor.fetchall()
                col_names = [col[2] for col in idx_cols]
                print(f"     Columns: {', '.join(col_names)}")
        else:
            print("  ⚠️  No indices found")
        
        print("\n" + "=" * 80)
        print("✅ SCHEMA FIX AND RESET COMPLETED")
        print("=" * 80)
        print("\nNEXT STEPS:")
        print("1. Restart the backend server")
        print("2. Upload zrsd002.xlsx via Data Management page")
        print("3. Verify: Upload same file again → Should skip duplicates")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema_and_reset()
