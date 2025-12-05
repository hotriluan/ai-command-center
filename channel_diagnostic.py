"""Simple channel diagnostic with file output"""
import sqlite3

conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

output = []
output.append("=== DISTINCT DIST VALUES ===")
cursor.execute("SELECT DISTINCT dist, COUNT(*) as count FROM sales_data GROUP BY dist ORDER BY count DESC LIMIT 20")
results = cursor.fetchall()

for row in results:
    dist_val = row[0]
    count = row[1]
    output.append(f"Value: {repr(dist_val):20} | Type: {type(dist_val).__name__:10} | Count: {count}")

output.append("\n=== MAPPING TEST ===")
CHANNEL_MAP = {
    '11': 'Industry',
    '13': 'Retail',
    '15': 'Project'
}

output.append(f"Map keys: {list(CHANNEL_MAP.keys())}")
output.append(f"Map key types: {[type(k).__name__ for k in CHANNEL_MAP.keys()]}")

output.append("\n=== SAMPLE MAPPING ===")
for row in results[:10]:
    dist_val = row[0]
    mapped = CHANNEL_MAP.get(dist_val, 'Others')
    str_mapped = CHANNEL_MAP.get(str(dist_val), 'Others')
    output.append(f"{repr(dist_val):15} -> Direct: {mapped:10} | As String: {str_mapped}")

conn.close()

# Write to file
with open('channel_diagnostic.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Output written to channel_diagnostic.txt")
