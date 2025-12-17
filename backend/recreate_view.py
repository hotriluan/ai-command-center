"""
Recreate view_sales_performance_v2 with correct collation
"""
from database import engine

connection = engine.raw_connection()
cursor = connection.cursor()

try:
    print("Dropping old view...")
    cursor.execute("DROP VIEW IF EXISTS view_sales_performance_v2")
    connection.commit()
    print("  ✅ Old view dropped")
    
    print("\nCreating new view...")
    
    create_view_sql = """
    CREATE VIEW view_sales_performance_v2 AS
    SELECT 
        s.salesman_name,
        s.year,
        s.month_number,
        CASE 
            WHEN s.month_number <= 6 THEN 1
            ELSE 2
        END as semester,
        SUM(s.net_value) as total_revenue,
        SUM(s.profit) as total_profit,
        COALESCE(t.target_amount, 0) as total_target,
        CASE 
            WHEN COALESCE(t.target_amount, 0) > 0 
            THEN (SUM(s.net_value) / t.target_amount) * 100
            ELSE 0
        END as achievement_percentage
    FROM sales_data s
    LEFT JOIN monthly_targets t 
        ON s.salesman_name COLLATE utf8mb4_unicode_ci = t.user_name COLLATE utf8mb4_unicode_ci
        AND s.year = t.year
        AND s.month_number = t.month_number
    WHERE s.salesman_name IS NOT NULL
    GROUP BY s.salesman_name, s.year, s.month_number, t.target_amount
    """
    
    cursor.execute(create_view_sql)
    connection.commit()
    print("  ✅ New view created")
    
    # Test the view
    print("\nTesting view...")
    cursor.execute("SELECT COUNT(*) FROM view_sales_performance_v2")
    count = cursor.fetchone()[0]
    print(f"  ✅ View has {count:,} rows")
    
    # Show sample
    cursor.execute("SELECT * FROM view_sales_performance_v2 LIMIT 3")
    print("\n  Sample rows:")
    for row in cursor.fetchall():
        print(f"    {row}")
    
    cursor.close()
    connection.close()
    
    print("\n✅ View recreation completed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    cursor.close()
    connection.close()
