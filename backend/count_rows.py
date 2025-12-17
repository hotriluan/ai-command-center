from database import engine

connection = engine.raw_connection()
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM sales_data")
count = cursor.fetchone()[0]
print(f"Total rows in sales_data: {count:,}")

cursor.close()
connection.close()
