"""
Debt & Credit Control Services
Handles AR Aging Report import and analysis
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from models import ARAgingReport

# Channel mapping for Distribution Channel codes
CHANNEL_MAP = {
    '11': 'Industry',
    '13': 'Retail',
    '15': 'Project'
}

def import_debt_data(file_contents: bytes, db: Session, report_date: str) -> Dict[str, Any]:
    """
    Import AR Aging Report from ZRFI005.XLSX
    Implements idempotent delete-insert pattern
    
    Args:
        file_contents: Excel file bytes
        db: Database session
        report_date: Report date in YYYY-MM-DD format
    
    Returns:
        Dict with status and statistics
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_contents, engine='openpyxl')
        
        # Delete existing records for this report_date (Idempotency)
        db.query(ARAgingReport).filter(ARAgingReport.report_date == report_date).delete()
        db.commit()
        
        # Process each row
        records_imported = 0
        for _, row in df.iterrows():
            # Map channel code to channel name
            channel_code = str(row.get('Distribution Channel', '')).strip()
            channel = CHANNEL_MAP.get(channel_code, 'Others')
            
            # Create record
            record = ARAgingReport(
                report_date=report_date,
                salesman_name=str(row.get('Salesman Name', '')).strip() if pd.notna(row.get('Salesman Name')) else None,
                customer_name=str(row.get('Customer Name', '')).strip(),
                customer_code=str(row.get('Customer Code', '')).strip(),
                channel=channel,
                total_debt=float(row.get('Total Target', 0)) if pd.notna(row.get('Total Target')) else 0,
                total_realization=float(row.get('Total Realization', 0)) if pd.notna(row.get('Total Realization')) else 0,
                debt_1_30=float(row.get('Target 1-30 Days', 0)) if pd.notna(row.get('Target 1-30 Days')) else 0,
                debt_31_60=float(row.get('Target 31-60 Days', 0)) if pd.notna(row.get('Target 31-60 Days')) else 0,
                debt_61_90=float(row.get('Target 61 - 90 Days', 0)) if pd.notna(row.get('Target 61 - 90 Days')) else 0,
                debt_91_120=float(row.get('Target 91 - 120 Days', 0)) if pd.notna(row.get('Target 91 - 120 Days')) else 0,
                debt_121_180=float(row.get('Target 121 - 180 Days', 0)) if pd.notna(row.get('Target 121 - 180 Days')) else 0,
                debt_over_180=float(row.get('Target > 180 Days', 0)) if pd.notna(row.get('Target > 180 Days')) else 0
            )
            
            db.add(record)
            records_imported += 1
        
        db.commit()
        
        return {
            "status": "success",
            "records_imported": records_imported,
            "report_date": report_date
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error importing debt data: {e}")
        import traceback
        traceback.print_exc()
        raise


def get_debt_overview(db: Session, report_date: str = None) -> Dict[str, Any]:
    """
    Get debt overview with KPIs and breakdowns
    Smart date defaulting: If no date provided, use latest available
    
    Returns:
        Dict with report_date, KPIs, channel_breakdown, aging_breakdown
    """
    try:
        # Smart Date Defaulting: Get latest report_date if not provided
        if not report_date:
            latest_date_result = db.query(func.max(ARAgingReport.report_date)).scalar()
            if not latest_date_result:
                return {
                    "status": "error",
                    "message": "No debt data available",
                    "report_date": None
                }
            report_date = latest_date_result
        
        # Query data for the report_date
        query = text("""
            SELECT 
                channel,
                SUM(total_debt) as total_debt,
                SUM(total_realization) as total_realization,
                SUM(debt_1_30) as debt_1_30,
                SUM(debt_31_60) as debt_31_60,
                SUM(debt_61_90) as debt_61_90,
                SUM(debt_91_120) as debt_91_120,
                SUM(debt_121_180) as debt_121_180,
                SUM(debt_over_180) as debt_over_180
            FROM ar_aging_report
            WHERE report_date = :report_date
            GROUP BY channel
        """)
        
        result = db.execute(query, {"report_date": report_date}).fetchall()
        
        if not result:
            return {
                "status": "error",
                "message": f"No data found for date {report_date}",
                "report_date": report_date
            }
        
        # Calculate KPIs
        total_debt = sum(float(row[1]) for row in result)
        total_realization = sum(float(row[2]) for row in result)
        bad_debt = sum(float(row[8]) for row in result)  # debt_over_180
        
        # Collection rate = Realization / Debt * 100
        collection_rate = (total_realization / total_debt * 100) if total_debt > 0 else 0
        
        # Channel breakdown for Collection Efficiency chart
        channel_breakdown = []
        for row in result:
            channel_breakdown.append({
                "channel": row[0],
                "outstanding": float(row[1]),
                "collected": float(row[2])
            })
        
        # Aging breakdown for Aging Structure chart
        aging_breakdown = {
            "1-30 Days": sum(float(row[3]) for row in result),
            "31-60 Days": sum(float(row[4]) for row in result),
            "61-90 Days": sum(float(row[5]) for row in result),
            "91-120 Days": sum(float(row[6]) for row in result),
            "121-180 Days": sum(float(row[7]) for row in result),
            ">180 Days": sum(float(row[8]) for row in result)
        }
        
        return {
            "status": "success",
            "report_date": report_date,
            "kpis": {
                "total_outstanding": total_debt,
                "total_collected": total_realization,
                "bad_debt": bad_debt,
                "collection_rate": round(collection_rate, 1)
            },
            "channel_breakdown": channel_breakdown,
            "aging_breakdown": aging_breakdown
        }
        
    except Exception as e:
        print(f"Error in get_debt_overview: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "report_date": report_date
        }


def get_top_debtors(db: Session, report_date: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top customers by outstanding debt
    Smart date defaulting: If no date provided, use latest available
    """
    try:
        # Smart Date Defaulting
        if not report_date:
            latest_date_result = db.query(func.max(ARAgingReport.report_date)).scalar()
            if not latest_date_result:
                return []
            report_date = latest_date_result
        
        # Query top debtors
        query = text("""
            SELECT 
                customer_name,
                customer_code,
                channel,
                total_debt,
                (debt_61_90 + debt_91_120 + debt_121_180 + debt_over_180) as overdue
            FROM ar_aging_report
            WHERE report_date = :report_date
            ORDER BY total_debt DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"report_date": report_date, "limit": limit}).fetchall()
        
        debtors = []
        for row in result:
            debtors.append({
                "customer_name": row[0],
                "customer_code": row[1],
                "channel": row[2],
                "total_debt": float(row[3]),
                "overdue": float(row[4])
            })
        
        return debtors
        
    except Exception as e:
        print(f"Error in get_top_debtors: {e}")
        import traceback
        traceback.print_exc()
        return []
