"""
Data Integrity Audit Script
Tests revenue vs target calculations
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from database import SessionLocal
from sqlalchemy import text
import pandas as pd

def audit_data_integrity():
    """
    Compare raw data vs view data for accuracy
    """
    db = SessionLocal()
    
    print("=" * 80)
    print("DATA INTEGRITY AUDIT - Revenue vs Target")
    print("=" * 80)
    
    try:
        # Test Case: Pick a specific salesman
        test_salesman = "NGUYỄN HỮU TUỆ"
        test_year = 2025
        test_month = 1
        
        print(f"\n[TEST CASE]")
        print(f"  Salesman: {test_salesman}")
        print(f"  Year: {test_year}")
        print(f"  Month: {test_month}")
        
        # CHECK 1: Raw sales_data
        print(f"\n[CHECK 1] Raw sales_data table")
        raw_query = text("""
            SELECT 
                COUNT(*) as row_count,
                SUM(net_value) as total_revenue
            FROM sales_data
            WHERE salesman_name = :name
            AND year = :year
            AND month_number = :month
        """)
        
        raw_result = db.execute(raw_query, {
            "name": test_salesman,
            "year": test_year,
            "month": test_month
        }).fetchone()
        
        print(f"  Row Count: {raw_result[0]}")
        print(f"  Total Revenue (Metric A): {raw_result[1]:,.2f}")
        
        # CHECK 2: View data
        print(f"\n[CHECK 2] view_sales_performance_v2")
        view_query = text("""
            SELECT 
                salesman_name,
                year,
                month_number,
                semester,
                total_revenue,
                total_profit,
                total_target,
                achievement_percentage
            FROM view_sales_performance_v2
            WHERE salesman_name = :name
            AND year = :year
            AND month_number = :month
        """)
        
        view_result = db.execute(view_query, {
            "name": test_salesman,
            "year": test_year,
            "month": test_month
        }).fetchone()
        
        if view_result:
            print(f"  Salesman: {view_result[0]}")
            print(f"  Year: {view_result[1]}")
            print(f"  Month: {view_result[2]}")
            print(f"  Semester: {view_result[3]}")
            print(f"  Total Revenue (Metric B): {view_result[4]:,.2f}")
            print(f"  Total Profit: {view_result[5]:,.2f}")
            print(f"  Total Target (Metric C): {view_result[6]:,.2f}")
            print(f"  Achievement %: {view_result[7]:.2f}%")
        else:
            print(f"  ❌ No data found in view!")
        
        # CHECK 3: Target table
        print(f"\n[CHECK 3] sales_target table")
        target_query = text("""
            SELECT 
                salesman_name,
                year,
                semester,
                target_amount
            FROM sales_target
            WHERE salesman_name = :name
            AND year = :year
        """)
        
        target_results = db.execute(target_query, {
            "name": test_salesman,
            "year": test_year
        }).fetchall()
        
        print(f"  Found {len(target_results)} target records:")
        for t in target_results:
            print(f"    - {t[0]} | Year {t[1]} | Semester {t[2]} | Target: {t[3]:,.2f}")
        
        # COMPARISON
        print(f"\n[COMPARISON]")
        if raw_result[1] and view_result:
            metric_a = raw_result[1]
            metric_b = view_result[4]
            metric_c = view_result[6]
            
            match = abs(metric_a - metric_b) < 0.01
            print(f"  Metric A (Raw): {metric_a:,.2f}")
            print(f"  Metric B (View): {metric_b:,.2f}")
            print(f"  Match: {'✅ YES' if match else '❌ NO'}")
            print(f"  Metric C (Target): {metric_c:,.2f}")
            
            if metric_c == 0:
                print(f"  ⚠️ WARNING: Target is ZERO!")
            
            # Check if target is multiplied
            if len(target_results) > 0:
                actual_target = target_results[0][3]
                if metric_c != actual_target:
                    ratio = metric_c / actual_target if actual_target > 0 else 0
                    print(f"  ⚠️ WARNING: View target ({metric_c:,.2f}) != Actual target ({actual_target:,.2f})")
                    print(f"  Ratio: {ratio:.2f}x (possibly multiplied by row count?)")
        
        # CHECK 4: Sample all salesmen
        print(f"\n[CHECK 4] Sample all salesmen for {test_year}")
        all_query = text("""
            SELECT 
                salesman_name,
                SUM(total_revenue) as revenue,
                SUM(total_target) as target,
                AVG(achievement_percentage) as achievement
            FROM view_sales_performance_v2
            WHERE year = :year
            GROUP BY salesman_name
            ORDER BY revenue DESC
            LIMIT 5
        """)
        
        all_results = db.execute(all_query, {"year": test_year}).fetchall()
        
        print(f"  Top 5 Salesmen:")
        for row in all_results:
            print(f"    {row[0][:20]:20} | Revenue: {row[1]:>15,.0f} | Target: {row[2]:>15,.0f} | Achievement: {row[3]:>6.1f}%")
        
        print("\n" + "=" * 80)
        print("AUDIT COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    audit_data_integrity()
