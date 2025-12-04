"""
Verification Test: Check monthly targets accuracy
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from database import SessionLocal
from sqlalchemy import text

def verify_migration():
    """Verify monthly targets are correct"""
    db = SessionLocal()
    
    print("=" * 80)
    print("VERIFICATION TEST - Monthly Targets Accuracy")
    print("=" * 80)
    
    try:
        # Test Case 1: Check a specific salesman
        test_name = "NGUYỄN HỮU TUỆ"
        test_year = 2025
        test_month = 1
        
        print(f"\n[TEST 1] Monthly Performance - {test_name}, {test_year}-{test_month:02d}")
        
        query = text("""
            SELECT 
                salesman_name,
                year,
                month_number,
                semester,
                total_revenue,
                total_target,
                achievement_percentage
            FROM view_sales_performance_v2
            WHERE salesman_name = :name
            AND year = :year
            AND month_number = :month
        """)
        
        result = db.execute(query, {
            "name": test_name,
            "year": test_year,
            "month": test_month
        }).fetchone()
        
        if result:
            print(f"  Salesman: {result[0]}")
            print(f"  Year: {result[1]}")
            print(f"  Month: {result[2]}")
            print(f"  Semester: {result[3]}")
            print(f"  Revenue: {result[4]:,.2f}")
            print(f"  Target: {result[5]:,.2f}")
            print(f"  Achievement: {result[6]:.2f}%")
            
            # Check if target is reasonable (should be ~1/6 of semester target)
            expected_monthly = 40_100_000_000 / 6
            actual_monthly = result[5]
            match = abs(expected_monthly - actual_monthly) < 1000
            
            print(f"\n  Expected Monthly Target: {expected_monthly:,.2f}")
            print(f"  Actual Monthly Target: {actual_monthly:,.2f}")
            print(f"  Match: {'✅ YES' if match else '❌ NO'}")
        
        # Test Case 2: Semester aggregation
        print(f"\n[TEST 2] Semester Performance - {test_name}, {test_year}, Semester 1")
        
        sem_query = text("""
            SELECT 
                salesman_name,
                semester,
                SUM(total_revenue) as total_revenue,
                SUM(total_target) as total_target,
                ROUND((SUM(total_revenue) * 1.0 / SUM(total_target)) * 100, 2) as achievement
            FROM view_sales_performance_v2
            WHERE salesman_name = :name
            AND year = :year
            AND semester = 1
            GROUP BY salesman_name, semester
        """)
        
        sem_result = db.execute(sem_query, {
            "name": test_name,
            "year": test_year
        }).fetchone()
        
        if sem_result:
            print(f"  Salesman: {sem_result[0]}")
            print(f"  Semester: {sem_result[1]}")
            print(f"  Total Revenue: {sem_result[2]:,.2f}")
            print(f"  Total Target: {sem_result[3]:,.2f}")
            print(f"  Achievement: {sem_result[4]:.2f}%")
            
            # Verify semester target = 6 months
            expected_semester = 40_100_000_000
            actual_semester = sem_result[3]
            match = abs(expected_semester - actual_semester) < 1000
            
            print(f"\n  Expected Semester Target: {expected_semester:,.2f}")
            print(f"  Actual Semester Target: {actual_semester:,.2f}")
            print(f"  Match: {'✅ YES' if match else '❌ NO'}")
        
        # Test Case 3: All salesmen summary
        print(f"\n[TEST 3] All Salesmen - Month {test_month}, {test_year}")
        
        all_query = text("""
            SELECT 
                salesman_name,
                total_revenue,
                total_target,
                achievement_percentage
            FROM view_sales_performance_v2
            WHERE year = :year
            AND month_number = :month
            ORDER BY total_revenue DESC
            LIMIT 5
        """)
        
        all_results = db.execute(all_query, {
            "year": test_year,
            "month": test_month
        }).fetchall()
        
        print(f"\n  Top 5 Salesmen:")
        for row in all_results:
            print(f"    {row[0][:25]:25} | Revenue: {row[1]:>15,.0f} | Target: {row[2]:>15,.0f} | Achievement: {row[3]:>6.1f}%")
        
        print("\n" + "=" * 80)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_migration()
