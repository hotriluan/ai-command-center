"""
Production Analytics Services
Handles lead time analysis and production efficiency metrics
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback

def get_production_lead_time_analysis(db: Session, 
                                       start_date: Optional[str] = None,
                                       end_date: Optional[str] = None,
                                       order_type: Optional[str] = None,
                                       mrp_filter: Optional[str] = None) -> Dict:
    """
    Calculate production lead time metrics with MTO/MTS lifecycle analysis
    
    Args:
        db: Database session
        start_date: Filter by release date (YYYY-MM-DD)
        end_date: Filter by release date (YYYY-MM-DD)
        order_type: Filter by order type (201S/201O)
        mrp_filter: Filter by MRP controller (P01/P02/P03)
    
    Returns:
        Dictionary containing:
        - summary_metrics: Overall averages
        - order_details: Individual order breakdowns with timeline segments
        - mto_lifecycle: MTO monthly lifecycle data (Prep, Production, Delivery)
        - mts_efficiency: MTS monthly production efficiency data
    """
    try:
        # STEP 1: Auto-detect end_date if not provided (fixes empty chart issue)
        if not end_date:
            max_date_query = text("SELECT MAX(actual_finish_date) as max_date FROM production_orders WHERE actual_finish_date IS NOT NULL")
            max_date_result = db.execute(max_date_query).fetchone()
            if max_date_result and max_date_result[0]:
                # Use the last day of the month containing the max date
                max_date = pd.to_datetime(max_date_result[0])
                end_date = (max_date + pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d')
                print(f"Auto-detected end_date: {end_date}")
        
        # STEP 2: Build query to JOIN production with sales_data for MTO orders
        query = """
            SELECT 
                p.order_id,
                p.plant,
                p.order_type,
                p.material_code,
                p.material_description,
                p.sales_order_id,
                p.release_date,
                p.actual_finish_date,
                p.batch,
                p.mrp_controller,
                p.order_qty,
                p.delivered_qty,
                p.unit,
                s.billing_date as so_billing_date,
                s.billing_document as so_number
            FROM production_orders p
            LEFT JOIN sales_data s ON CONVERT(p.sales_order_id, CHAR) = CONVERT(s.billing_document, CHAR)
            WHERE p.actual_finish_date IS NOT NULL
              AND p.release_date IS NOT NULL
        """
        
        params = {}
        
        if start_date:
            query += " AND p.release_date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND p.release_date <= :end_date"
            params['end_date'] = end_date
            
        if order_type:
            query += " AND p.order_type = :order_type"
            params['order_type'] = order_type
        
        if mrp_filter:
            query += " AND p.mrp_controller = :mrp_filter"
            params['mrp_filter'] = mrp_filter
        
        # Execute query
        df = pd.read_sql(text(query), db.get_bind(), params=params)
        
        if df.empty:
            return {
                "status": "success",
                "message": "No production data found for the specified filters",
                "data": {
                    "summary_metrics": {},
                    "order_details": [],
                    "mto_lifecycle": [],
                    "mts_efficiency": []
                }
            }
        
        # STEP 3: Convert date columns to datetime
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['actual_finish_date'] = pd.to_datetime(df['actual_finish_date'], errors='coerce')
        df['so_billing_date'] = pd.to_datetime(df['so_billing_date'], errors='coerce')
        
        # STEP 4: Calculate Timeline Segments based on Order Type
        def calculate_segments(row):
            """Calculate Prep, Production, Delivery times based on order type"""
            prep_time = 0
            production_time = 0
            delivery_time = 0
            
            if row['order_type'] == '201O':  # Make-To-Order
                # Production Time (always calculated)
                production_time = (row['actual_finish_date'] - row['release_date']).days
                
                # Prep Time = SO Date to Release Date (use billing_date as SO date proxy)
                if pd.notna(row['so_billing_date']):
                    prep_time = (row['release_date'] - row['so_billing_date']).days
                    prep_time = max(0, prep_time)  # Clamp to 0 if negative
                
                # Delivery Time = Finish to Billing
                if pd.notna(row['so_billing_date']):
                    delivery_time = (row['so_billing_date'] - row['actual_finish_date']).days
                    delivery_time = max(0, delivery_time)  # Clamp to 0 if negative
            
            elif row['order_type'] == '201S':  # Make-To-Stock
                # Only Production Time
                production_time = (row['actual_finish_date'] - row['release_date']).days
                prep_time = 0
                delivery_time = 0
            
            return pd.Series({
                'prep_time': prep_time,
                'production_time': production_time,
                'delivery_time': delivery_time,
                'total_lead_time': prep_time + production_time + delivery_time
            })
        
        # Apply segment calculation
        df[['prep_time', 'production_time', 'delivery_time', 'total_lead_time']] = df.apply(calculate_segments, axis=1)
        
        # STEP 5: Calculate Yield Metrics
        df['yield_variance'] = df['delivered_qty'] - df['order_qty']
        df['yield_rate'] = (df['delivered_qty'] / df['order_qty'] * 100).fillna(0)
        
        # Classify yield status
        def classify_yield(rate):
            if pd.isna(rate):
                return 'unknown'
            elif rate >= 100:
                return 'excellent'
            elif rate >= 95:
                return 'good'
            elif rate >= 90:
                return 'acceptable'
            else:
                return 'poor'
        
        df['yield_status'] = df['yield_rate'].apply(classify_yield)
        
        # STEP 6: Summary Metrics
        summary_metrics = {
            "total_orders": int(len(df)),
            "mts_orders": int((df['order_type'] == '201S').sum()),
            "mto_orders": int((df['order_type'] == '201O').sum()),
            "avg_prep_time": round(df['prep_time'].mean(), 1),
            "avg_production_time": round(df['production_time'].mean(), 1),
            "avg_delivery_time": round(df['delivery_time'].mean(), 1),
            "avg_total_lead_time": round(df['total_lead_time'].mean(), 1),
            "avg_yield_rate": round(df['yield_rate'].mean(), 2),
            "total_order_qty": round(df['order_qty'].sum(), 2),
            "total_delivered_qty": round(df['delivered_qty'].sum(), 2),
            "yield_variance_total": round(df['yield_variance'].sum(), 2)
        }
        
        # Yield distribution
        yield_distribution = df['yield_status'].value_counts().to_dict()
        summary_metrics['yield_distribution'] = {
            'excellent': yield_distribution.get('excellent', 0),
            'good': yield_distribution.get('good', 0),
            'acceptable': yield_distribution.get('acceptable', 0),
            'poor': yield_distribution.get('poor', 0),
            'unknown': yield_distribution.get('unknown', 0)
        }
        
        # STEP 7: Order Details (top 100 with timeline segments)
        order_details = []
        df_sorted = df.sort_values('yield_variance', ascending=True).head(100)  # Worst yields first
        
        for _, row in df_sorted.iterrows():
            # Create timeline summary
            timeline_parts = []
            if row['prep_time'] > 0:
                timeline_parts.append(f"Prep: {int(row['prep_time'])}d")
            timeline_parts.append(f"Prod: {int(row['production_time'])}d")
            if row['delivery_time'] > 0:
                timeline_parts.append(f"Deliv: {int(row['delivery_time'])}d")
            timeline_summary = " | ".join(timeline_parts)
            
            order_details.append({
                "order_id": row['order_id'],
                "order_type": row['order_type'],
                "material_code": row['material_code'],
                "material_description": row['material_description'],
                "sales_order_id": row['sales_order_id'],
                "mrp_controller": row['mrp_controller'],
                "release_date": row['release_date'].strftime('%Y-%m-%d') if pd.notna(row['release_date']) else None,
                "actual_finish_date": row['actual_finish_date'].strftime('%Y-%m-%d') if pd.notna(row['actual_finish_date']) else None,
                "prep_time": int(row['prep_time']),
                "production_time": int(row['production_time']),
                "delivery_time": int(row['delivery_time']),
                "total_lead_time": int(row['total_lead_time']),
                "timeline_summary": timeline_summary,
                "order_qty": round(row['order_qty'], 2) if pd.notna(row['order_qty']) else 0,
                "delivered_qty": round(row['delivered_qty'], 2) if pd.notna(row['delivered_qty']) else 0,
                "yield_variance": round(row['yield_variance'], 2),
                "yield_rate": round(row['yield_rate'], 2) if pd.notna(row['yield_rate']) else 0,
                "yield_status": row['yield_status']
            })
        
        # STEP 8: MTO Lifecycle Data (Monthly aggregation with 3 segments)
        df['year_month'] = df['release_date'].dt.to_period('M').astype(str)
        df_mto = df[df['order_type'] == '201O']
        
        mto_lifecycle = []
        if not df_mto.empty:
            mto_monthly = df_mto.groupby('year_month').agg({
                'prep_time': 'mean',
                'production_time': 'mean',
                'delivery_time': 'mean',
                'order_id': 'count'
            }).reset_index()
            
            for _, row in mto_monthly.iterrows():
                mto_lifecycle.append({
                    "month": row['year_month'],
                    "month_name": pd.to_datetime(row['year_month']).strftime('%b %Y'),
                    "prep_time": round(row['prep_time'], 1),
                    "production_time": round(row['production_time'], 1),
                    "delivery_time": round(row['delivery_time'], 1),
                    "order_count": int(row['order_id'])
                })
        
        # STEP 9: MTS Efficiency Data (Monthly aggregation - production time only)
        df_mts = df[df['order_type'] == '201S']
        
        mts_efficiency = []
        if not df_mts.empty:
            mts_monthly = df_mts.groupby('year_month').agg({
                'production_time': 'mean',
                'order_id': 'count'
            }).reset_index()
            
            for _, row in mts_monthly.iterrows():
                mts_efficiency.append({
                    "month": row['year_month'],
                    "month_name": pd.to_datetime(row['year_month']).strftime('%b %Y'),
                    "production_time": round(row['production_time'], 1),
                    "order_count": int(row['order_id'])
                })
        
        return {
            "status": "success",
            "data": {
                "summary_metrics": summary_metrics,
                "order_details": order_details,
                "mto_lifecycle": mto_lifecycle,
                "mts_efficiency": mts_efficiency
            }
        }
    
    except Exception as e:
        print(f"Error in production lead time analysis: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "data": {
                "summary_metrics": {},
                "order_details": [],
                "mto_lifecycle": [],
                "mts_efficiency": []
            }
        }


def get_mrp_controller_performance(db: Session) -> List[Dict]:
    """
    Analyze performance by MRP Controller
    
    Returns list of controller metrics including:
    - Average lead time
    - Average yield rate
    - Total orders managed
    """
    try:
        query = text("""
            SELECT 
                mrp_controller,
                COUNT(*) as total_orders,
                AVG(JULIANDAY(actual_finish_date) - JULIANDAY(release_date)) as avg_lead_time,
                AVG((delivered_qty / NULLIF(order_qty, 0)) * 100) as avg_yield_rate,
                SUM(order_qty) as total_order_qty,
                SUM(delivered_qty) as total_delivered_qty
            FROM production_orders
            WHERE mrp_controller IS NOT NULL
              AND release_date IS NOT NULL
              AND actual_finish_date IS NOT NULL
            GROUP BY mrp_controller
            ORDER BY total_orders DESC
        """)
        
        result = db.execute(query).fetchall()
        
        performance_data = []
        for row in result:
            performance_data.append({
                "mrp_controller": row[0],
                "total_orders": row[1],
                "avg_lead_time": round(row[2], 1) if row[2] else 0,
                "avg_yield_rate": round(row[3], 2) if row[3] else 0,
                "total_order_qty": round(row[4], 2) if row[4] else 0,
                "total_delivered_qty": round(row[5], 2) if row[5] else 0
            })
        
        return performance_data
    
    except Exception as e:
        print(f"Error in MRP controller performance analysis: {e}")
        traceback.print_exc()
        return []


def get_material_lead_time_analysis(db: Session, top_n: int = 20) -> List[Dict]:
    """
    Analyze lead times by material (product)
    
    Args:
        db: Database session
        top_n: Number of top materials by order count
    
    Returns:
        List of material metrics
    """
    try:
        query = text(f"""
            SELECT 
                material_code,
                material_description,
                COUNT(*) as order_count,
                AVG(JULIANDAY(actual_finish_date) - JULIANDAY(release_date)) as avg_lead_time,
                MIN(JULIANDAY(actual_finish_date) - JULIANDAY(release_date)) as min_lead_time,
                MAX(JULIANDAY(actual_finish_date) - JULIANDAY(release_date)) as max_lead_time,
                AVG((delivered_qty / NULLIF(order_qty, 0)) * 100) as avg_yield_rate
            FROM production_orders
            WHERE material_code IS NOT NULL
              AND release_date IS NOT NULL
              AND actual_finish_date IS NOT NULL
            GROUP BY material_code, material_description
            ORDER BY order_count DESC
            LIMIT {top_n}
        """)
        
        result = db.execute(query).fetchall()
        
        material_data = []
        for row in result:
            material_data.append({
                "material_code": row[0],
                "material_description": row[1],
                "order_count": row[2],
                "avg_lead_time": round(row[3], 1) if row[3] else 0,
                "min_lead_time": int(row[4]) if row[4] else 0,
                "max_lead_time": int(row[5]) if row[5] else 0,
                "avg_yield_rate": round(row[6], 2) if row[6] else 0
            })
        
        return material_data
    
    except Exception as e:
        print(f"Error in material lead time analysis: {e}")
        traceback.print_exc()
        return []
