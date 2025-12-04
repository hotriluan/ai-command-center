"""
Duplication Audit Script
Checks database schema, indices, and duplicate records
"""
import sqlite3
import os

def audit_duplicates():
    """Comprehensive audit of duplication issues"""
    db_path = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
    
    print("=" * 80)
    print("DUPLICATION AUDIT - Sales Data Import")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # CHECK 1: Database Schema & Indices
        print("\n[CHECK 1] Database Schema & Indices")
        print("-" * 80)
        
        # 1a. Table schema
        print("\n1a. sales_data table schema:")
        cursor.execute("PRAGMA table_info(sales_data)")
        columns = cursor.fetchall()
        for col in columns:
            pk = " (PRIMARY KEY)" if col[5] == 1 else ""
            print(f"  {col[1]:20} {col[2]:10} {pk}")
        
        # 1b. Check for indices
        print("\n1b. Indices on sales_data:")
        cursor.execute("PRAGMA index_list('sales_data')")
        indices = cursor.fetchall()
        
        if indices:
            for idx in indices:
                idx_name = idx[1]
                is_unique = "UNIQUE" if idx[2] == 1 else "NON-UNIQUE"
                print(f"  {idx_name}: {is_unique}")
                
                # Get index details
                cursor.execute(f"PRAGMA index_info('{idx_name}')")
                idx_cols = cursor.fetchall()
                col_names = [col[2] for col in idx_cols]
                print(f"    Columns: {', '.join(col_names)}")
        else:
            print("  ⚠️ NO INDICES FOUND!")
        
        # 1c. Check for billing_document/billing_item columns
        print("\n1c. Check for billing_document/billing_item columns:")
        col_names = [col[1] for col in columns]
        has_billing_doc = 'billing_document' in col_names
        has_billing_item = 'billing_item' in col_names
        
        print(f"  billing_document: {'✅ EXISTS' if has_billing_doc else '❌ MISSING'}")
        print(f"  billing_item: {'✅ EXISTS' if has_billing_item else '❌ MISSING'}")
        
        # 1d. Check for actual duplicates
        print("\n1d. Checking for duplicate records:")
        
        # Since billing_document/billing_item don't exist, check by other fields
        cursor.execute("""
            SELECT 
                salesman_name, 
                description, 
                net_value, 
                COUNT(*) as count
            FROM sales_data
            GROUP BY salesman_name, description, net_value, month_number, year
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"  ⚠️ Found {len(duplicates)} duplicate groups:")
            for dup in duplicates[:5]:
                print(f"    {dup[0][:30]:30} | {dup[1][:30]:30} | {dup[2]:>12,.0f} | Count: {dup[3]}")
        else:
            print("  ✅ No duplicates found")
        
        # 1e. Total record count
        cursor.execute("SELECT COUNT(*) FROM sales_data")
        total = cursor.fetchone()[0]
        print(f"\n1e. Total records in sales_data: {total:,}")
        
        # CHECK 2: Sample data to understand structure
        print("\n[CHECK 2] Sample Data Structure")
        print("-" * 80)
        
        cursor.execute("SELECT * FROM sales_data LIMIT 3")
        samples = cursor.fetchall()
        
        if samples:
            print(f"\nFirst 3 records:")
            for i, row in enumerate(samples, 1):
                print(f"\n  Record {i}:")
                for j, col in enumerate(columns):
                    col_name = col[1]
                    value = row[j]
                    print(f"    {col_name:20} = {value}")
        
        # CHECK 3: Count by year
        print("\n[CHECK 3] Record Distribution by Year")
        print("-" * 80)
        
        cursor.execute("""
            SELECT year, COUNT(*) as count
            FROM sales_data
            GROUP BY year
            ORDER BY year DESC
        """)
        
        year_counts = cursor.fetchall()
        for year, count in year_counts:
            print(f"  {year}: {count:,} records")
        
        print("\n" + "=" * 80)
        print("AUDIT COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    audit_duplicates()
