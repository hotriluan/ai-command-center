import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/command_center.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_view():
    db = SessionLocal()
    try:
        sql = """
        DROP VIEW IF EXISTS view_sales_performance;
        DROP VIEW IF EXISTS view_sales_performance_v2;

        CREATE VIEW view_sales_performance_v2 AS
        SELECT 
            s.salesman_name as user_name, -- Renamed to match analytics_services expectation (user_name) or fix analytics_services?
            -- Wait, analytics_services uses user_name, but the SQL I read uses salesman_name.
            -- Let's check the SQL file again.
            -- Line 11: s.salesman_name,
            -- Line 36: LEFT JOIN monthly_targets mt ON s.salesman_name = mt.user_name
            
            -- analytics_services.py:
            -- SELECT user_name, ... FROM view_sales_performance_v2
            
            -- So the view MUST return a column named 'user_name'.
            -- But the SQL file I read returns 'salesman_name'.
            -- Line 11: s.salesman_name,
            
            -- I should ALIAS it in the view definition to match analytics_services expectation?
            -- Or change analytics_services to use salesman_name?
            
            -- Let's look at the SQL file content again carefully.
            -- It says: s.salesman_name,
            
            -- If I create it as is, the column will be 'salesman_name'.
            -- analytics_services queries 'user_name'.
            -- This will cause an error "no such column: user_name".
            
            -- I should probably fix the view definition to alias it as user_name OR fix the code.
            -- Given "user_name" is used in monthly_targets, maybe "user_name" is preferred?
            -- But "sales_data" has "salesman_name".
            
            -- Let's check services.py. It queries:
            -- SELECT salesman_name ... FROM view_sales_performance_v2
            
            -- So services.py expects 'salesman_name'.
            -- analytics_services.py expects 'user_name'.
            
            -- This is a mismatch.
            -- I should probably include BOTH or alias one.
            -- Or fix analytics_services.py to use salesman_name.
            
            -- Let's stick to the SQL file content first, but maybe I should modify it to be compatible.
            -- Actually, let's just run the SQL as provided in the file first, and see if debug_waterfall fails with column error.
            -- Wait, I can just read the file and execute it.
            
            -- But wait, if services.py expects salesman_name and analytics_services expects user_name, one of them is wrong.
            -- services.py:
            -- 170:                 salesman_name,
            
            -- analytics_services.py:
            -- 74:                 user_name,
            
            -- So they ARE different.
            -- I will modify the view to return `s.salesman_name as user_name` AND `s.salesman_name`.
            -- Or just `s.salesman_name` and fix analytics_services.py.
            -- Fixing code is safer than changing schema if schema is standard.
            -- But this is a view.
            
            -- Let's just execute the SQL file as is, and then if debug_waterfall fails, I will fix analytics_services.py.
            -- Because services.py seems to be the main one.
            
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
        GROUP BY s.salesman_name, s.year, s.month_number;
        """
        
        # Split by ; and execute
        commands = sql.split(';')
        for cmd in commands:
            if cmd.strip():
                db.execute(text(cmd))
        
        db.commit()
        print("View created successfully.")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_view()
