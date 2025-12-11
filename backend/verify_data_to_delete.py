
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import SalesData
import sys
import os

# Add current directory to path so we can import models
sys.path.append(os.getcwd())

DATABASE_URL = "sqlite:///./command_center_v2.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def check_data():
    try:
        count = session.query(SalesData).filter(
            SalesData.year == 2025,
            SalesData.month_number == 12
        ).count()
        
        print(f"Found {count} records for Dec 2025")
        
        if count > 0:
            sample = session.query(SalesData).filter(
                SalesData.year == 2025,
                SalesData.month_number == 12
            ).first()
            print(f"Sample record: ID={sample.id}, Date={sample.year}-{sample.month}, Value={sample.net_value}")
    except Exception as e:
        print(f"Error querying database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data()
