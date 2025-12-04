"""
Year-aware utility functions for dashboard
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

def get_available_years(db: Session):
    """
    Get list of distinct years from sales_data
    Returns: List of years in descending order
    """
    try:
        query = text("SELECT DISTINCT year FROM sales_data WHERE year IS NOT NULL ORDER BY year DESC")
        result = db.execute(query)
        years = [row[0] for row in result.fetchall()]
        return years
    except:
        return []

def get_default_year(db: Session):
    """
    Get default year (latest year in database or current year)
    """
    years = get_available_years(db)
    if years:
        return years[0]  # Latest year
    return datetime.now().year  # Fallback to current year

def get_dashboard_stats_by_year(db: Session, year: int = None):
    """
    Get dashboard statistics filtered by year
    If year is None, use default year
    """
    if year is None:
        year = get_default_year(db)
    
    try:
        # KPI Calculations
        kpi_query = text("""
            SELECT 
                SUM(net_value) as total_revenue,
                SUM(profit) as total_profit,
                SUM(marketing_spend) as total_marketing
            FROM sales_data
            WHERE year = :year
        """)
        
        kpi_result = db.execute(kpi_query, {"year": year}).fetchone()
        
        revenue = kpi_result[0] or 0
        profit = kpi_result[1] or 0
        marketing = kpi_result[2] or 0
        margin = (profit / revenue * 100) if revenue > 0 else 0
        
        # Growth calculations (compare with previous year)
        prev_year_query = text("""
            SELECT 
                SUM(net_value) as prev_revenue,
                SUM(profit) as prev_profit
            FROM sales_data
            WHERE year = :prev_year
        """)
        
        prev_result = db.execute(prev_year_query, {"prev_year": year - 1}).fetchone()
        prev_revenue = prev_result[0] or 0
        prev_profit = prev_result[1] or 0
        
        revenue_growth = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        profit_growth = ((profit - prev_profit) / prev_profit * 100) if prev_profit > 0 else 0
        
        # Monthly Trend
        monthly_query = text("""
            SELECT 
                month_number,
                month,
                SUM(net_value) as revenue,
                SUM(profit) as profit
            FROM sales_data
            WHERE year = :year
            GROUP BY month_number, month
            ORDER BY month_number
        """)
        
        monthly_result = db.execute(monthly_query, {"year": year}).fetchall()
        monthly_trend = [
            {
                "name": row[1] or f"Month {row[0]}",
                "revenue": float(row[2] or 0),
                "profit": float(row[3] or 0)
            }
            for row in monthly_result
        ]
        
        # Channel Distribution
        channel_query = text("""
            SELECT 
                dist as channel,
                SUM(net_value) as value
            FROM sales_data
            WHERE year = :year AND dist IS NOT NULL
            GROUP BY dist
            ORDER BY value DESC
            LIMIT 10
        """)
        
        channel_result = db.execute(channel_query, {"year": year}).fetchall()
        channel_distribution = [
            {"name": row[0], "value": float(row[1] or 0)}
            for row in channel_result
        ]
        
        # Branch Distribution
        branch_query = text("""
            SELECT 
                branch,
                SUM(net_value) as value
            FROM sales_data
            WHERE year = :year AND branch IS NOT NULL
            GROUP BY branch
            ORDER BY value DESC
            LIMIT 10
        """)
        
        branch_result = db.execute(branch_query, {"year": year}).fetchall()
        branch_distribution = [
            {"name": row[0], "value": float(row[1] or 0)}
            for row in branch_result
        ]
        
        # Top Products
        product_query = text("""
            SELECT 
                description,
                SUM(net_value) as value
            FROM sales_data
            WHERE year = :year AND description IS NOT NULL
            GROUP BY description
            ORDER BY value DESC
            LIMIT 10
        """)
        
        product_result = db.execute(product_query, {"year": year}).fetchall()
        top_products = [
            {"name": row[0], "value": float(row[1] or 0)}
            for row in product_result
        ]
        
        # Top Salesmen
        salesman_query = text("""
            SELECT 
                salesman_name,
                SUM(net_value) as value
            FROM sales_data
            WHERE year = :year AND salesman_name IS NOT NULL
            GROUP BY salesman_name
            ORDER BY value DESC
            LIMIT 10
        """)
        
        salesman_result = db.execute(salesman_query, {"year": year}).fetchall()
        top_salesmen = [
            {"name": row[0], "value": float(row[1] or 0)}
            for row in salesman_result
        ]
        
        # Sales Performance (from view) - Grouped by Semester
        performance_query = text("""
            SELECT 
                salesman_name,
                semester,
                SUM(total_revenue) as revenue,
                SUM(total_target) as target,
                CASE 
                    WHEN SUM(total_target) > 0 
                    THEN (SUM(total_revenue) * 1.0 / SUM(total_target)) * 100
                    ELSE 0 
                END as achievement
            FROM view_sales_performance_v2
            WHERE year = :year
            GROUP BY salesman_name, semester
            ORDER BY salesman_name, semester
        """)
        
        performance_result = db.execute(performance_query, {"year": year}).fetchall()
        
        # Group by salesman and create semester entries
        salesman_data = {}
        for row in performance_result:
            name = row[0]
            semester = row[1]
            
            if name not in salesman_data:
                salesman_data[name] = []
            
            salesman_data[name].append({
                "name": f"{name}",
                "semester": semester,
                "actual": float(row[2] or 0),
                "target": float(row[3] or 0),
                "rate": float(row[4] or 0),
                "status": "success" if row[4] >= 100 else ("warning" if row[4] >= 80 else "destructive")
            })
        
        # Flatten to list
        sales_performance = []
        for name, semesters in salesman_data.items():
            sales_performance.extend(semesters)
        
        return {
            "year": year,
            "kpi": {
                "revenue": revenue,
                "revenue_growth": revenue_growth,
                "profit": profit,
                "profit_growth": profit_growth,
                "marketing": marketing,
                "margin": margin
            },
            "charts": {
                "monthly_trend": monthly_trend,
                "channel_distribution": channel_distribution,
                "branch_distribution": branch_distribution,
                "top_products": top_products,
                "top_salesmen": top_salesmen
            },
            "sales_performance": sales_performance
        }
        
    except Exception as e:
        print(f"Error in get_dashboard_stats_by_year: {e}")
        import traceback
        traceback.print_exc()
        return None
