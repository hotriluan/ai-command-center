"""
Analytics Services
Provides advanced analytics endpoints for the Analytics page
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any


def get_product_matrix(db: Session, year: int = None, semester: int = None) -> List[Dict[str, Any]]:
    """
    Product Portfolio Matrix - Bubble Chart Data
    Returns: Revenue (x), Profit Margin % (y), Quantity (z), Product Name
    LIMITED TO TOP 50 PRODUCTS for readability
    Supports semester filtering: None (whole year), 1 (Jan-Jun), 2 (Jul-Dec)
    """
    try:
        # Build query to join sales_data with product_cost
        # LIMIT to TOP 50 by revenue
        query = text("""
            SELECT 
                sd.description as product_name,
                SUM(sd.net_value) as total_revenue,
                SUM(sd.billing_qty) as total_quantity,
                SUM(sd.profit) as total_profit
            FROM sales_data sd
            WHERE (:year IS NULL OR sd.year = :year)
              AND (:semester IS NULL OR 
                   (CASE WHEN sd.month_number <= 6 THEN 1 ELSE 2 END) = :semester)
            GROUP BY sd.description
            HAVING total_revenue > 0
            ORDER BY total_revenue DESC
            LIMIT 50
        """)
        
        result = db.execute(query, {'year': year, 'semester': semester}).fetchall()
        
        products = []
        for row in result:
            product_name = row[0]
            revenue = float(row[1])
            quantity = float(row[2])
            profit = float(row[3])
            
            # Calculate profit margin %
            margin = (profit / revenue * 100) if revenue > 0 else 0
            
            products.append({
                'name': product_name,
                'revenue': revenue,
                'margin': round(margin, 2),
                'quantity': quantity,
                'profit': profit
            })
        
        return products
        
    except Exception as e:
        print(f"Error in get_product_matrix: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_target_waterfall(db: Session, year: int = None, semester: int = None) -> List[Dict[str, Any]]:
    """
    Sales Efficiency Leaderboard
    Returns salespeople ranked by achievement percentage (descending)
    Supports semester filtering: None (whole year), 1 (Jan-Jun), 2 (Jul-Dec)
    """
    try:
        # Query sales performance view with NULL handling
        query = text("""
            SELECT 
                salesman_name,
                COALESCE(SUM(total_revenue), 0) as actual,
                COALESCE(SUM(total_target), 0) as target
            FROM view_sales_performance_v2
            WHERE (:year IS NULL OR year = :year)
              AND (:semester IS NULL OR semester = :semester)
            GROUP BY salesman_name
            HAVING target > 0
            ORDER BY salesman_name
        """)
        
        result = db.execute(query, {'year': year, 'semester': semester}).fetchall()
        
        if not result:
            return []
        
        # Build leaderboard with achievement rates
        leaderboard = []
        for row in result:
            name = row[0]
            actual = float(row[1])
            target = float(row[2])
            
            # Calculate achievement rate
            achievement_rate = (actual / target * 100) if target > 0 else 0
            
            # Determine status
            if achievement_rate >= 100:
                status = "success"
            elif achievement_rate >= 80:
                status = "warning"
            else:
                status = "danger"
            
            leaderboard.append({
                'name': name,
                'actual': actual,
                'target': target,
                'achievement_rate': round(achievement_rate, 1),
                'status': status
            })
        
        # Sort by achievement rate descending (best performers first)
        leaderboard.sort(key=lambda x: x['achievement_rate'], reverse=True)
        
        return leaderboard
        
    except Exception as e:
        print(f"Error in get_target_waterfall: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_seasonality_heatmap(db: Session, year: int = None, semester: int = None) -> List[Dict[str, Any]]:
    """
    Seasonality Heatmap Data
    Returns revenue by Year x Month for pattern analysis
    Supports semester filtering: None (whole year), 1 (Jan-Jun), 2 (Jul-Dec)
    """
    try:
        # Query revenue by year and month
        query = text("""
            SELECT 
                year,
                month_number,
                SUM(net_value) as revenue
            FROM sales_data
            WHERE (:year IS NULL OR year = :year)
              AND (:semester IS NULL OR 
                   (CASE WHEN month_number <= 6 THEN 1 ELSE 2 END) = :semester)
            GROUP BY year, month_number
            ORDER BY year, month_number
        """)
        
        result = db.execute(query, {'year': year, 'semester': semester}).fetchall()
        
        heatmap_data = []
        for row in result:
            heatmap_data.append({
                'year': int(row[0]),
                'month': int(row[1]),
                'revenue': float(row[2])
            })
        
        return heatmap_data
        
    except Exception as e:
        print(f"Error in get_seasonality_heatmap: {e}")
        import traceback
        traceback.print_exc()
        return []
