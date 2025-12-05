import sqlite3
import os

# Check both database locations
dbs = [
    'command_center_v2.db',
    'backend/command_center_v2.db',
    './command_center_v2.db',
    './backend/command_center_v2.db'
]

print("=== CHECKING ALL DATABASE LOCATIONS ===\n")

for db_path in dbs:
    if os.path.exists(db_path):
        print(f"✓ Found: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check row count
            cursor.execute('SELECT COUNT(*) FROM sales_data')
            count = cursor.fetchone()[0]
            print(f"  Rows in sales_data: {count:,}")
            
            if count > 0:
                # Check distinct dist values
                cursor.execute('SELECT DISTINCT dist FROM sales_data LIMIT 10')
                dist_values = [r[0] for r in cursor.fetchall()]
                print(f"  Sample dist values: {dist_values}")
                
                # Test CASE WHEN
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN CAST(dist AS TEXT) LIKE '%11%' THEN 'Industry'
                            WHEN CAST(dist AS TEXT) LIKE '%13%' THEN 'Retail'
                            WHEN CAST(dist AS TEXT) LIKE '%15%' THEN 'Project'
                            ELSE 'Others' 
                        END as channel,
                        COUNT(*) as count
                    FROM sales_data
                    GROUP BY channel
                """)
                results = cursor.fetchall()
                print(f"  Channel mapping results:")
                for channel, cnt in results:
                    print(f"    {channel}: {cnt:,} rows")
            
            conn.close()
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print(f"✗ Not found: {db_path}")
    
    print()
