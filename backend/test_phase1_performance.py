"""
Performance Test Suite - Phase 1 Verification
Tests the performance improvements from Phase 1 optimizations
"""

import time
import sys
from database import SessionLocal
from sqlalchemy import text

def test_dashboard_query_performance():
    """Test dashboard query performance with new indexes"""
    print("\n" + "=" * 80)
    print("TEST 1: Dashboard Query Performance")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Test 1: Year-filtered KPI query
        print("\n[Test 1.1] Year-filtered KPI aggregation...")
        start = time.time()
        
        query = text("""
            SELECT 
                SUM(net_value) as total_revenue,
                SUM(profit) as total_profit,
                SUM(marketing_spend) as total_marketing
            FROM sales_data
            WHERE year = 2024
        """)
        
        result = db.execute(query).fetchone()
        elapsed = time.time() - start
        
        print(f"  ⏱️  Query time: {elapsed:.3f}s")
        print(f"  📊 Result: Revenue={result[0]:,.0f}, Profit={result[1]:,.0f}")
        
        if elapsed < 1.0:
            print("  ✅ PASS: Query completed in < 1s")
        else:
            print(f"  ⚠️  WARNING: Query took {elapsed:.3f}s (expected < 1s)")
        
        # Test 1.2: Monthly aggregation with indexes
        print("\n[Test 1.2] Monthly trend aggregation...")
        start = time.time()
        
        query = text("""
            SELECT 
                month_number,
                month,
                SUM(net_value) as revenue,
                SUM(profit) as profit
            FROM sales_data
            WHERE year = 2024
            GROUP BY month_number, month
            ORDER BY month_number
        """)
        
        result = db.execute(query).fetchall()
        elapsed = time.time() - start
        
        print(f"  ⏱️  Query time: {elapsed:.3f}s")
        print(f"  📊 Months found: {len(result)}")
        
        if elapsed < 0.5:
            print("  ✅ PASS: Query completed in < 0.5s")
        else:
            print(f"  ⚠️  WARNING: Query took {elapsed:.3f}s (expected < 0.5s)")
        
        # Test 1.3: Branch distribution (new index)
        print("\n[Test 1.3] Branch distribution aggregation...")
        start = time.time()
        
        query = text("""
            SELECT 
                branch,
                SUM(net_value) as value
            FROM sales_data
            WHERE year = 2024 AND branch IS NOT NULL
            GROUP BY branch
            ORDER BY value DESC
            LIMIT 10
        """)
        
        result = db.execute(query).fetchall()
        elapsed = time.time() - start
        
        print(f"  ⏱️  Query time: {elapsed:.3f}s")
        print(f"  📊 Branches found: {len(result)}")
        
        if elapsed < 0.5:
            print("  ✅ PASS: Query completed in < 0.5s")
        else:
            print(f"  ⚠️  WARNING: Query took {elapsed:.3f}s (expected < 0.5s)")
        
    finally:
        db.close()

def test_analytics_query_performance():
    """Test analytics queries with new indexes"""
    print("\n" + "=" * 80)
    print("TEST 2: Analytics Query Performance")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Test 2.1: Product matrix (description index)
        print("\n[Test 2.1] Product portfolio matrix...")
        start = time.time()
        
        query = text("""
            SELECT 
                description as product_name,
                SUM(net_value) as total_revenue,
                SUM(billing_qty) as total_quantity,
                SUM(profit) as total_profit
            FROM sales_data
            WHERE year = 2024
            GROUP BY description
            HAVING total_revenue > 0
            ORDER BY total_revenue DESC
            LIMIT 50
        """)
        
        result = db.execute(query).fetchall()
        elapsed = time.time() - start
        
        print(f"  ⏱️  Query time: {elapsed:.3f}s")
        print(f"  📊 Products found: {len(result)}")
        
        if elapsed < 1.0:
            print("  ✅ PASS: Query completed in < 1s")
        else:
            print(f"  ⚠️  WARNING: Query took {elapsed:.3f}s (expected < 1s)")
        
        # Test 2.2: Seasonality heatmap (composite index)
        print("\n[Test 2.2] Seasonality heatmap...")
        start = time.time()
        
        query = text("""
            SELECT 
                year,
                month_number,
                SUM(net_value) as revenue
            FROM sales_data
            WHERE year IN (2023, 2024)
            GROUP BY year, month_number
            ORDER BY year, month_number
        """)
        
        result = db.execute(query).fetchall()
        elapsed = time.time() - start
        
        print(f"  ⏱️  Query time: {elapsed:.3f}s")
        print(f"  📊 Data points: {len(result)}")
        
        if elapsed < 0.5:
            print("  ✅ PASS: Query completed in < 0.5s")
        else:
            print(f"  ⚠️  WARNING: Query took {elapsed:.3f}s (expected < 0.5s)")
        
    finally:
        db.close()

def test_debt_query_performance():
    """Test debt analysis queries with new indexes"""
    print("\n" + "=" * 80)
    print("TEST 3: Debt Analysis Query Performance")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Get latest report date
        latest_date = db.execute(text("SELECT MAX(report_date) FROM ar_aging_report")).scalar()
        
        if not latest_date:
            print("  ⏭️  SKIPPED: No debt data available")
            return
        
        print(f"\n  Using report_date: {latest_date}")
        
        # Test 3.1: Channel breakdown (composite index)
        print("\n[Test 3.1] Channel breakdown by date...")
        start = time.time()
        
        query = text("""
            SELECT 
                channel,
                SUM(total_debt) as total_debt,
                SUM(total_realization) as total_realization
            FROM ar_aging_report
            WHERE report_date = :report_date
            GROUP BY channel
        """)
        
        result = db.execute(query, {"report_date": latest_date}).fetchall()
        elapsed = time.time() - start
        
        print(f"  ⏱️  Query time: {elapsed:.3f}s")
        print(f"  📊 Channels found: {len(result)}")
        
        if elapsed < 0.3:
            print("  ✅ PASS: Query completed in < 0.3s")
        else:
            print(f"  ⚠️  WARNING: Query took {elapsed:.3f}s (expected < 0.3s)")
        
    finally:
        db.close()

def verify_indexes():
    """Verify that all indexes were created"""
    print("\n" + "=" * 80)
    print("INDEX VERIFICATION")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        expected_indexes = {
            'sales_data': [
                'idx_sales_month_number',
                'idx_sales_branch',
                'idx_sales_description',
                'idx_sales_year_month',
                'idx_sales_description_year'
            ],
            'monthly_targets': [
                'idx_monthly_year',
                'idx_monthly_month_number',
                'idx_monthly_target_lookup'
            ],
            'ar_aging_report': [
                'idx_debt_salesman',
                'idx_debt_channel',
                'idx_debt_date_channel'
            ]
        }
        
        all_passed = True
        
        for table, indexes in expected_indexes.items():
            print(f"\n{table}:")
            
            for index_name in indexes:
                query = text("""
                    SELECT COUNT(*) 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE() 
                    AND table_name = :table 
                    AND index_name = :index
                """)
                
                result = db.execute(query, {"table": table, "index": index_name}).scalar()
                
                if result > 0:
                    print(f"  ✅ {index_name}")
                else:
                    print(f"  ❌ {index_name} - MISSING!")
                    all_passed = False
        
        if all_passed:
            print("\n✅ All indexes verified successfully!")
        else:
            print("\n⚠️  Some indexes are missing. Run migrate_add_indexes.py")
        
        return all_passed
        
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PHASE 1 PERFORMANCE TEST SUITE")
    print("=" * 80)
    
    try:
        # First verify indexes
        if not verify_indexes():
            print("\n⚠️  WARNING: Not all indexes are present. Results may not reflect optimizations.")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(0)
        
        # Run performance tests
        test_dashboard_query_performance()
        test_analytics_query_performance()
        test_debt_query_performance()
        
        print("\n" + "=" * 80)
        print("✅ PERFORMANCE TESTS COMPLETED")
        print("=" * 80)
        print("\n💡 Next steps:")
        print("   1. Compare these results with baseline (before optimization)")
        print("   2. If performance is good, proceed to Phase 2 optimizations")
        print("   3. Monitor production performance after deployment")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
