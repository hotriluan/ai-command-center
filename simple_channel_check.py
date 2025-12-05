"""Simple channel diagnostic"""
import sqlite3

conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

print("=== DISTINCT DIST VALUES ===")
cursor.execute("SELECT DISTINCT dist, COUNT(*) as count FROM sales_data GROUP BY dist ORDER BY count DESC LIMIT 20")
results = cursor.fetchall()

for row in results:
    dist_val = row[0]
    count = row[1]
    print(f"Value: {repr(dist_val):20} | Type: {type(dist_val).__name__:10} | Count: {count}")

print("\n=== MAPPING TEST ===")
CHANNEL_MAP = {
    '11': 'Industry',
    '13': 'Retail',
    '15': 'Project'
}

print(f"Map keys: {list(CHANNEL_MAP.keys())}")
print(f"Map key types: {[type(k) for k in CHANNEL_MAP.keys()]}")

print("\n=== SAMPLE MAPPING ===")
for row in results[:10]:
    dist_val = row[0]
    mapped = CHANNEL_MAP.get(dist_val, 'Others')
    str_mapped = CHANNEL_MAP.get(str(dist_val), 'Others')
    print(f"{repr(dist_val):15} -> Direct: {mapped:10} | As String: {str_mapped}")

conn.close()
