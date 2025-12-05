import sqlite3
conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

print("=== CHECKING ACTUAL DIST VALUES ===\n")

# Get distinct dist values with counts
cursor.execute("""
    SELECT dist, COUNT(*) as count 
    FROM sales_data 
    GROUP BY dist 
    ORDER BY count DESC
""")

results = cursor.fetchall()
print(f"Found {len(results)} distinct dist values:\n")

for dist_val, count in results:
    print(f"Value: {repr(dist_val):20} Type: {type(dist_val).__name__:10} Count: {count:,}")

# Test the CASE WHEN logic
print("\n=== TESTING CASE WHEN LOGIC ===\n")

for dist_val, count in results[:10]:  # Test first 10
    # Test current logic
    cast_val = str(dist_val) if dist_val else ""
    
    if '%11%' in cast_val or '11' in cast_val:
        mapped = 'Industry'
    elif '%13%' in cast_val or '13' in cast_val:
        mapped = 'Retail'
    elif '%15%' in cast_val or '15' in cast_val:
        mapped = 'Project'
    else:
        mapped = 'Others'
    
    print(f"{repr(dist_val):20} -> {mapped:10} (Count: {count:,})")

# Test actual SQL CASE WHEN
print("\n=== TESTING ACTUAL SQL CASE WHEN ===\n")

cursor.execute("""
    SELECT 
        dist,
        CASE 
            WHEN CAST(dist AS TEXT) LIKE '%11%' THEN 'Industry'
            WHEN CAST(dist AS TEXT) LIKE '%13%' THEN 'Retail'
            WHEN CAST(dist AS TEXT) LIKE '%15%' THEN 'Project'
            ELSE 'Others' 
        END as channel_name,
        COUNT(*) as count
    FROM sales_data
    GROUP BY dist
    ORDER BY count DESC
    LIMIT 20
""")

results = cursor.fetchall()
for dist_val, channel, count in results:
    print(f"{repr(dist_val):20} -> {channel:10} (Count: {count:,})")

conn.close()
