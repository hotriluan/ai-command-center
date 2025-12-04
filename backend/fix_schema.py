import sqlite3

conn = sqlite3.connect('command_center.db')
cursor = conn.cursor()

print("Checking current schema...")
cursor.execute("PRAGMA table_info(sales_data)")
current_cols = [row[1] for row in cursor.fetchall()]
print(f"Current columns: {current_cols}")

if 'id' in current_cols:
    print("✅ id column already exists!")
else:
    print("Adding id column...")
    
    # Create new table with id
    cursor.execute('''
        CREATE TABLE sales_data_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT,
            month_number INTEGER,
            year INTEGER,
            dist TEXT,
            branch TEXT,
            salesman_name TEXT,
            product_group TEXT,
            description TEXT,
            net_value REAL,
            profit REAL,
            marketing_spend REAL,
            customer_name TEXT,
            billing_qty REAL
        )
    ''')
    
    # Copy data from old table
    cursor.execute('''
        INSERT INTO sales_data_new 
        (month, month_number, year, dist, branch, salesman_name, product_group, 
         description, net_value, profit, marketing_spend, customer_name, billing_qty)
        SELECT month, month_number, year, dist, branch, salesman_name, product_group,
               description, net_value, profit, marketing_spend, customer_name, billing_qty
        FROM sales_data
    ''')
    
    # Drop old table
    cursor.execute('DROP TABLE sales_data')
    
    # Rename new table
    cursor.execute('ALTER TABLE sales_data_new RENAME TO sales_data')
    
    conn.commit()
    print("✅ Successfully added id column!")

# Verify
cursor.execute("PRAGMA table_info(sales_data)")
final_cols = [row[1] for row in cursor.fetchall()]
print(f"Final columns: {final_cols}")

cursor.execute("SELECT COUNT(*) FROM sales_data")
count = cursor.fetchone()[0]
print(f"Total rows: {count}")

conn.close()
