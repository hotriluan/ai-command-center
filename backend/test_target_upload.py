"""
Test Target Upload with Semester-to-Month Splitting
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from database import SessionLocal
from sqlalchemy import text
import pandas as pd
import io

def test_target_upload():
    """Test the new target upload logic"""
    db = SessionLocal()
    
    print("=" * 80)
    print("TEST: Target Upload - Semester to Monthly Splitting")
    print("=" * 80)
    
    try:
        # Create test data
        test_data = {
            'Salesman Name': ['NGUYỄN HỮU TUỆ', 'NGUYỄN HỮU TUỆ'],
            'Year': [2025, 2025],
            'Semester': [1, 2],
            'Target': [40_100_000_000, 40_100_000_000]
        }
        
        df = pd.DataFrame(test_data)
        
        print("\n[TEST DATA]")
        print(df.to_string(index=False))
        
        # Simulate upload logic
        print("\n[PROCESSING]")
        
        updated_count = 0
        for _, row in df.iterrows():
            name = str(row['Salesman Name']).strip()
            semester = int(row['Semester'])
            semester_target = float(row['Target'])
            year = int(row['Year'])
            
            # Calculate monthly target
            monthly_target = semester_target / 6.0
            
            # Determine months
            if semester == 1:
                months = [1, 2, 3, 4, 5, 6]
            else:
                months = [7, 8, 9, 10, 11, 12]
            
            print(f"\n  {name} - {year} Semester {semester}")
            print(f"  Semester Target: {semester_target:,.0f}")
            print(f"  Monthly Target: {monthly_target:,.0f}")
            print(f"  Months: {months}")
            
            # Upsert for each month
            for month_num in months:
                upsert_query = text("""
                    INSERT INTO monthly_targets (user_name, year, month_number, target_amount, semester)
                    VALUES (:user_name, :year, :month_number, :target_amount, :semester)
                    ON CONFLICT(user_name, year, month_number) 
                    DO UPDATE SET 
                        target_amount = excluded.target_amount,
                        semester = excluded.semester
                """)
                
                db.execute(upsert_query, {
                    'user_name': name,
                    'year': year,
                    'month_number': month_num,
                    'target_amount': monthly_target,
                    'semester': semester
                })
                
                updated_count += 1
        
        db.commit()
        
        print(f"\n  ✅ Inserted/Updated {updated_count} monthly records")
        
        # Verify
        print("\n[VERIFICATION]")
        
        verify_query = text("""
            SELECT user_name, year, month_number, semester, target_amount
            FROM monthly_targets
            WHERE user_name = :name AND year = :year
            ORDER BY month_number
        """)
        
        results = db.execute(verify_query, {
            'name': 'NGUYỄN HỮU TUỆ',
            'year': 2025
        }).fetchall()
        
        print(f"\n  Monthly targets for NGUYỄN HỮU TUỆ (2025):")
        for r in results:
            print(f"    Month {r[2]:2}: Semester {r[3]} | Target: {r[4]:,.0f}")
        
        # Check totals
        print("\n[TOTALS CHECK]")
        
        total_query = text("""
            SELECT 
                semester,
                SUM(target_amount) as total
            FROM monthly_targets
            WHERE user_name = :name AND year = :year
            GROUP BY semester
        """)
        
        totals = db.execute(total_query, {
            'name': 'NGUYỄN HỮU TUỆ',
            'year': 2025
        }).fetchall()
        
        for t in totals:
            print(f"  Semester {t[0]}: {t[1]:,.0f} (should be 40,100,000,000)")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_target_upload()
