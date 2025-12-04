from database import SessionLocal, SalesData, ProductCost, SalesTarget
from sqlalchemy import text

def check_data():
    db = SessionLocal()
    try:
        sales_count = db.query(SalesData).count()
        cost_count = db.query(ProductCost).count()
        target_count = db.query(SalesTarget).count()
        
        print(f"SalesData rows: {sales_count}")
        print(f"ProductCost rows: {cost_count}")
        print(f"SalesTarget rows: {target_count}")
        
        if sales_count > 0:
            first_sale = db.query(SalesData).first()
            print(f"Sample Sale: Revenue={first_sale.revenue}, Profit={first_sale.profit}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
