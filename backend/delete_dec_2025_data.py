
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

def delete_data():
    try:
        # Pre-check
        count_before = session.query(SalesData).filter(
            SalesData.year == 2025,
            SalesData.month_number == 12
        ).count()
        
        print(f"PRE-CHECK: Found {count_before} records to delete for Dec 2025")
        
        if count_before == 0:
            print("No data to delete.")
            return

        # Delete
        print("Deleting records...")
        deleted_count = session.query(SalesData).filter(
            SalesData.year == 2025,
            SalesData.month_number == 12
        ).delete(synchronize_session=False)
        
        session.commit()
        print(f"Successfully deleted {deleted_count} records.")
        
        # Post-check
        count_after = session.query(SalesData).filter(
            SalesData.year == 2025,
            SalesData.month_number == 12
        ).count()
        
        print(f"POST-CHECK: Remaining records for Dec 2025: {count_after}")
        
        if count_after == 0:
            print("VERIFICATION SUCCESSFUL: All targeted data has been removed.")
        else:
            print("VERIFICATION FAILED: Some data remains.")

    except Exception as e:
        print(f"Error during deletion: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    delete_data()
