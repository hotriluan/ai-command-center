
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db, engine
from models import ARAgingReport

def verify():
    print("Initializing DB...")
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
            
        print("Adding records to session WITH FLUSH...")
        for r in records:
            db.add(r)
            db.flush() # This is the fix
            
        print("Committing (should succeed)...")
        db.commit()
        print("Commit SUCCESS! Fix verified.")
        
    except Exception as e:
        print(f"\nCaught unexpected exception:\n{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    verify()
