from database import engine, Base, SalesData
from sqlalchemy import text

def reset_sales_table():
    print("Resetting SalesData table...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS sales_data"))
        print("Dropped sales_data table.")
    
    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables recreated.")

if __name__ == "__main__":
    reset_sales_table()
