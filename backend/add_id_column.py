"""
Add ID column as primary key to sales_data table
"""
from database import engine

def add_id_column():
    connection = engine.raw_connection()
    cursor = connection.cursor()
    
    try:
        print("Adding ID column as primary key...")
        
        # Add id column as first column with auto_increment
        sql = "ALTER TABLE sales_data ADD COLUMN `id` INT AUTO_INCREMENT PRIMARY KEY FIRST"
        
        cursor.execute(sql)
        connection.commit()
        
        print("✅ ID column added successfully!")
        
        # Verify
        cursor.execute("SHOW COLUMNS FROM sales_data")
        print("\nUpdated schema:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} {row[2]} {row[3]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        cursor.close()
        connection.close()

if __name__ == "__main__":
    add_id_column()
