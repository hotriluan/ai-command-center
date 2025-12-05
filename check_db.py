"""Check database schema and data"""
import sqlite3

conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

output = []

# Check tables
output.append("=== DATABASE TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    output.append(f"Table: {table[0]}")

# Check sales_data table
output.append("\n=== SALES_DATA TABLE INFO ===")
try:
    cursor.execute("SELECT COUNT(*) FROM sales_data")
    count = cursor.fetchone()[0]
    output.append(f"Total rows: {count}")
    
    if count > 0:
        # Get column names
        cursor.execute("PRAGMA table_info(sales_data)")
        columns = cursor.fetchall()
        output.append("\nColumns:")
        for col in columns:
            output.append(f"  {col[1]} ({col[2]})")
        
        # Get sample data
        output.append("\n=== SAMPLE DATA (first 5 rows) ===")
        cursor.execute("SELECT dist, net_value, year FROM sales_data LIMIT 5")
        samples = cursor.fetchall()
        for row in samples:
            output.append(f"dist={repr(row[0])}, net_value={row[1]}, year={row[2]}")
        
        # Get distinct dist values
        output.append("\n=== DISTINCT DIST VALUES ===")
        cursor.execute("SELECT dist, COUNT(*) as cnt FROM sales_data GROUP BY dist ORDER BY cnt DESC")
        dist_values = cursor.fetchall()
        for row in dist_values:
            output.append(f"dist={repr(row[0]):15} type={type(row[0]).__name__:10} count={row[1]}")
            
except Exception as e:
    output.append(f"Error: {e}")

conn.close()

# Write output
with open('db_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('\n'.join(output))
