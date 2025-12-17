"""
Production Analytics Services
Provides MTO timeline, MTS efficiency, and quantity variance analysis
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List, Optional, Any
from datetime import datetime, date

def get_mto_timeline_analysis(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    mrp_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze MTO (Make-to-Order) production timeline
    Tracks: SO Date → Release Date → Actual Finish Date → Billing Date
    """
    
    # Build WHERE clause
    where_conditions = ["po.order_type = '201O'"]  # MTO only
    
    if start_date:
        where_conditions.append(f"po.release_date >= '{start_date}'")
    if end_date:
        where_conditions.append(f"po.release_date <= '{end_date}'")
    if mrp_filter and mrp_filter != 'All':
        where_conditions.append(f"po.mrp_controller = '{mrp_filter}'")
    
    where_clause = " AND ".join(where_conditions)
    
    # Main query: Join production_orders with sales_data
    query = text(f"""
        SELECT 
            po.order_id,
            po.material_description,
            po.sales_order_id,
            sd.so_date,
            po.release_date,
            po.actual_finish_date,
            sd.billing_date,
            po.order_qty,
            po.delivered_qty,
            po.mrp_controller,
            po.system_status,
            -- Calculate time segments (in days)
            DATEDIFF(po.release_date, sd.so_date) as prep_days,
            DATEDIFF(po.actual_finish_date, po.release_date) as production_days,
            DATEDIFF(sd.billing_date, po.actual_finish_date) as delivery_days,
            DATEDIFF(sd.billing_date, sd.so_date) as total_cycle_days,
            -- Calculate yield
            CASE 
                WHEN po.order_qty > 0 THEN (po.delivered_qty / po.order_qty * 100)
                ELSE 0
            END as yield_rate
        FROM production_orders po
        LEFT JOIN sales_data sd ON po.sales_order_id = sd.so_no
        WHERE {where_clause}
            AND sd.so_date IS NOT NULL
            AND po.release_date IS NOT NULL
            AND po.actual_finish_date IS NOT NULL
            AND sd.billing_date IS NOT NULL
        ORDER BY po.release_date DESC
        LIMIT 500
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    # Process data
    orders = []
    total_prep = 0
    total_production = 0
    total_delivery = 0
    total_cycle = 0
    total_yield = 0
    count = 0
    
    for row in rows:
        order = {
            'order_id': row[0],
            'material': row[1],
            'so_id': row[2],
            'so_date': str(row[3]) if row[3] else None,
            'release_date': str(row[4]) if row[4] else None,
            'finish_date': str(row[5]) if row[5] else None,
            'billing_date': str(row[6]) if row[6] else None,
            'order_qty': float(row[7]) if row[7] else 0,
            'delivered_qty': float(row[8]) if row[8] else 0,
            'mrp_controller': row[9],
            'status': row[10],
            'prep_days': int(row[11]) if row[11] else 0,
            'production_days': int(row[12]) if row[12] else 0,
            'delivery_days': int(row[13]) if row[13] else 0,
            'total_cycle_days': int(row[14]) if row[14] else 0,
            'yield_rate': float(row[15]) if row[15] else 0
        }
        orders.append(order)
        
        # Accumulate for averages
        if row[11]: total_prep += row[11]
        if row[12]: total_production += row[12]
        if row[13]: total_delivery += row[13]
        if row[14]: total_cycle += row[14]
        if row[15]: total_yield += row[15]
        count += 1
    
    # Calculate summary metrics
    summary = {
        'total_orders': count,
        'avg_prep_days': round(total_prep / count, 1) if count > 0 else 0,
        'avg_production_days': round(total_production / count, 1) if count > 0 else 0,
        'avg_delivery_days': round(total_delivery / count, 1) if count > 0 else 0,
        'avg_total_cycle_days': round(total_cycle / count, 1) if count > 0 else 0,
        'avg_yield_rate': round(total_yield / count, 1) if count > 0 else 0
    }
    
    # Timeline breakdown by phase
    timeline_breakdown = [
        {'phase': 'Preparation', 'avg_days': summary['avg_prep_days'], 'description': 'SO Date → Release'},
        {'phase': 'Production', 'avg_days': summary['avg_production_days'], 'description': 'Release → Finish'},
        {'phase': 'Delivery', 'avg_days': summary['avg_delivery_days'], 'description': 'Finish → Billing'}
    ]
    
    return {
        'status': 'success',
        'summary': summary,
        'timeline_breakdown': timeline_breakdown,
        'orders': orders[:100]  # Return top 100 for display
    }


def get_mts_production_analysis(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    mrp_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze MTS (Make-to-Stock) production efficiency
    Tracks: Basic Start Date → Release Date → Actual Finish Date
    """
    
    # Build WHERE clause
    where_conditions = ["po.order_type = '201S'"]  # MTS only
    
    if start_date:
        where_conditions.append(f"po.release_date >= '{start_date}'")
    if end_date:
        where_conditions.append(f"po.release_date <= '{end_date}'")
    if mrp_filter and mrp_filter != 'All':
        where_conditions.append(f"po.mrp_controller = '{mrp_filter}'")
    
    where_clause = " AND ".join(where_conditions)
    
    query = text(f"""
        SELECT 
            po.order_id,
            po.material_description,
            po.basic_start_date,
            po.release_date,
            po.actual_finish_date,
            po.order_qty,
            po.delivered_qty,
            po.mrp_controller,
            po.system_status,
            -- Calculate time segments
            DATEDIFF(po.release_date, po.basic_start_date) as planning_days,
            DATEDIFF(po.actual_finish_date, po.release_date) as production_days,
            DATEDIFF(po.actual_finish_date, po.basic_start_date) as total_lead_time,
            -- Calculate yield
            CASE 
                WHEN po.order_qty > 0 THEN (po.delivered_qty / po.order_qty * 100)
                ELSE 0
            END as yield_rate
        FROM production_orders po
        WHERE {where_clause}
            AND po.basic_start_date IS NOT NULL
            AND po.release_date IS NOT NULL
            AND po.actual_finish_date IS NOT NULL
        ORDER BY po.release_date DESC
        LIMIT 500
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    # Process data
    orders = []
    total_planning = 0
    total_production = 0
    total_lead_time = 0
    total_yield = 0
    count = 0
    
    for row in rows:
        order = {
            'order_id': row[0],
            'material': row[1],
            'basic_start': str(row[2]) if row[2] else None,
            'release_date': str(row[3]) if row[3] else None,
            'finish_date': str(row[4]) if row[4] else None,
            'order_qty': float(row[5]) if row[5] else 0,
            'delivered_qty': float(row[6]) if row[6] else 0,
            'mrp_controller': row[7],
            'status': row[8],
            'planning_days': int(row[9]) if row[9] else 0,
            'production_days': int(row[10]) if row[10] else 0,
            'total_lead_time': int(row[11]) if row[11] else 0,
            'yield_rate': float(row[12]) if row[12] else 0
        }
        orders.append(order)
        
        # Accumulate
        if row[9]: total_planning += row[9]
        if row[10]: total_production += row[10]
        if row[11]: total_lead_time += row[11]
        if row[12]: total_yield += row[12]
        count += 1
    
    # Summary
    summary = {
        'total_orders': count,
        'avg_planning_days': round(total_planning / count, 1) if count > 0 else 0,
        'avg_production_days': round(total_production / count, 1) if count > 0 else 0,
        'avg_total_lead_time': round(total_lead_time / count, 1) if count > 0 else 0,
        'avg_yield_rate': round(total_yield / count, 1) if count > 0 else 0
    }
    
    # MRP Controller performance
    mrp_performance = {}
    for order in orders:
        mrp = order['mrp_controller']
        if mrp not in mrp_performance:
            mrp_performance[mrp] = {
                'orders': 0,
                'total_lead_time': 0,
                'total_yield': 0
            }
        mrp_performance[mrp]['orders'] += 1
        mrp_performance[mrp]['total_lead_time'] += order['total_lead_time']
        mrp_performance[mrp]['total_yield'] += order['yield_rate']
    
    mrp_stats = []
    for mrp, stats in mrp_performance.items():
        mrp_stats.append({
            'mrp_controller': mrp,
            'total_orders': stats['orders'],
            'avg_lead_time': round(stats['total_lead_time'] / stats['orders'], 1),
            'avg_yield': round(stats['total_yield'] / stats['orders'], 1)
        })
    
    return {
        'status': 'success',
        'summary': summary,
        'mrp_performance': mrp_stats,
        'orders': orders[:100]
    }


def get_quantity_variance_analysis(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    order_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze quantity variance: Order Qty vs Delivered Qty
    """
    
    # Build WHERE clause
    where_conditions = ["1=1"]
    
    if start_date:
        where_conditions.append(f"po.release_date >= '{start_date}'")
    if end_date:
        where_conditions.append(f"po.release_date <= '{end_date}'")
    if order_type and order_type != 'All':
        where_conditions.append(f"po.order_type = '{order_type}'")
    
    where_clause = " AND ".join(where_conditions)
    
    query = text(f"""
        SELECT 
            po.order_id,
            po.order_type,
            po.material_description,
            po.release_date,
            po.actual_finish_date,
            po.order_qty,
            po.delivered_qty,
            po.unit,
            po.mrp_controller,
            -- Calculate variance
            (po.delivered_qty - po.order_qty) as variance_qty,
            CASE 
                WHEN po.order_qty > 0 THEN ((po.delivered_qty - po.order_qty) / po.order_qty * 100)
                ELSE 0
            END as variance_pct,
            CASE 
                WHEN po.order_qty > 0 THEN (po.delivered_qty / po.order_qty * 100)
                ELSE 0
            END as fulfillment_rate
        FROM production_orders po
        WHERE {where_clause}
            AND po.order_qty > 0
            AND po.delivered_qty IS NOT NULL
        ORDER BY ABS(po.delivered_qty - po.order_qty) DESC
        LIMIT 500
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    # Process
    orders = []
    perfect_match = 0
    over_production = 0
    under_production = 0
    total_variance_pct = 0
    
    for row in rows:
        variance_pct = float(row[10]) if row[10] else 0
        
        order = {
            'order_id': row[0],
            'order_type': row[1],
            'material': row[2],
            'release_date': str(row[3]) if row[3] else None,
            'finish_date': str(row[4]) if row[4] else None,
            'order_qty': float(row[5]) if row[5] else 0,
            'delivered_qty': float(row[6]) if row[6] else 0,
            'unit': row[7],
            'mrp_controller': row[8],
            'variance_qty': float(row[9]) if row[9] else 0,
            'variance_pct': variance_pct,
            'fulfillment_rate': float(row[11]) if row[11] else 0,
            'status': 'Perfect' if abs(variance_pct) < 1 else ('Over' if variance_pct > 0 else 'Under')
        }
        orders.append(order)
        
        # Categorize
        if abs(variance_pct) < 1:
            perfect_match += 1
        elif variance_pct > 0:
            over_production += 1
        else:
            under_production += 1
        
        total_variance_pct += abs(variance_pct)
    
    count = len(orders)
    
    summary = {
        'total_orders': count,
        'perfect_match': perfect_match,
        'over_production': over_production,
        'under_production': under_production,
        'perfect_match_rate': round(perfect_match / count * 100, 1) if count > 0 else 0,
        'avg_variance_pct': round(total_variance_pct / count, 1) if count > 0 else 0
    }
    
    # Variance distribution
    variance_distribution = [
        {'category': 'Perfect Match (<1%)', 'count': perfect_match},
        {'category': 'Over Production (>1%)', 'count': over_production},
        {'category': 'Under Production (<-1%)', 'count': under_production}
    ]
    
    return {
        'status': 'success',
        'summary': summary,
        'variance_distribution': variance_distribution,
        'orders': orders[:100]
    }
