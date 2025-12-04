import sqlite3

conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print("=" * 80)
print("DATABASE SCHEMA INSPECTION REPORT")
print("=" * 80)

for table in tables:
    print(f"\n{'='*80}")
    print(f"TABLE: {table}")
    print(f"{'='*80}")
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    print(f"\n{'Column Name':<25} {'Type':<15} {'PK':<5} {'NotNull':<8} {'Default':<15}")
    print("-" * 80)
    for col in columns:
        cid, name, dtype, notnull, default, pk = col
        default_val = str(default) if default else ''
        print(f"{name:<25} {dtype:<15} {pk:<5} {notnull:<8} {default_val:<15}")
    
    # Get indexes
    cursor.execute(f"PRAGMA index_list({table})")
    indexes = cursor.fetchall()
    if indexes:
        print(f"\nIndexes:")
        for idx in indexes:
            idx_name = idx[1]
            is_unique = idx[2]
            cursor.execute(f"PRAGMA index_info({idx_name})")
            idx_cols = cursor.fetchall()
            cols = [c[2] for c in idx_cols]
            unique_str = "UNIQUE" if is_unique else "NON-UNIQUE"
            print(f"  - {idx_name} ({unique_str}): {', '.join(cols)}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"\nRow Count: {count:,}")

conn.close()
