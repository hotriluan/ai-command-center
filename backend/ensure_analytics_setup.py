"""
Ensure Analytics Setup Script
Verifies that view_sales_performance_v2 exists and creates it if missing
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./command_center_v2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def ensure_view_exists():
    db = SessionLocal()
    try:
        # Check if view exists
        print("Checking if view_sales_performance_v2 exists...")
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name='view_sales_performance_v2'
        """)).fetchone()
        
        if result:
            print("✓ View exists")
            # Test query
            test_result = db.execute(text("""
                SELECT COUNT(*) FROM view_sales_performance_v2
            """)).fetchone()
            print(f"✓ View has {test_result[0]} rows")
        else:
            print("✗ View does not exist. Creating...")
            
            # Drop old views
            db.execute(text("DROP VIEW IF EXISTS view_sales_performance"))
            db.execute(text("DROP VIEW IF EXISTS view_sales_performance_v2"))
            
            # Create view
            create_sql = """
            CREATE VIEW view_sales_performance_v2 AS
            SELECT 
                s.salesman_name,
                s.year,
                s.month_number,
                CASE WHEN s.month_number <= 6 THEN 1 ELSE 2 END as semester,
                SUM(s.net_value) as total_revenue,
                SUM(s.net_value - (s.billing_qty * COALESCE(pc.cogs, 0))) as total_profit,
                COALESCE(MAX(mt.target_amount), 0) as total_target,
                CASE 
                    WHEN COALESCE(MAX(mt.target_amount), 0) > 0 
                    THEN ROUND((SUM(s.net_value) * 1.0 / MAX(mt.target_amount)) * 100, 2)
                    ELSE 0 
                END as achievement_percentage
            FROM sales_data s
            LEFT JOIN product_cost pc ON s.description = pc.description
            LEFT JOIN monthly_targets mt ON s.salesman_name = mt.user_name 
                                         AND s.year = mt.year 
                                         AND s.month_number = mt.month_number
            GROUP BY s.salesman_name, s.year, s.month_number
            """
            
            db.execute(text(create_sql))
            db.commit()
            print("✓ View created successfully")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    ensure_view_exists()
