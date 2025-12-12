
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db, engine
from models import ARAgingReport
from sqlalchemy.orm import Session
from sqlalchemy import text

def reproduce():
    print("Initializing DB...")
    # Ensure tables exist
    init_db()
    
    db = SessionLocal()
    try:
        print("Cleaning up old test data...")
        db.query(ARAgingReport).filter(ARAgingReport.report_date == '9999-12-31').delete()
        db.commit()
        
        print("Creating dummy records...")
        records = []
        for i in range(5):
            rec = ARAgingReport(
                report_date='9999-12-31',
                customer_name=f'Test Cust {i}',
                customer_code=f'TEST{i}',
                channel='Test',
                total_debt=100.0
            )
            records.append(rec)
            
        print("Adding records to session...")
        for r in records:
            db.add(r)
            
        print("Committing (this should fail)...")
        db.commit()
        print("Commit SUCCESS (Unexpected!)")
        
    except Exception as e:
        print(f"\nCaught expected exception:\n{e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
