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
        # Fix FutureWarning: Wrap bytes in BytesIO
        from io import BytesIO
        df = pd.read_excel(BytesIO(file_contents), engine='openpyxl')
        
        print(f"Initial rows loaded: {len(df)}")
        
        # ===== ROBUST DATA CLEANING =====
        # Step 1: Drop completely empty rows
        df.dropna(how='all', inplace=True)
        print(f"After dropping empty rows: {len(df)}")
        
        # Step 2: Strict Data Cleaning (User Request)
        # Drop rows where Critical Keys are missing. 
        # Using 'Customer Code' and 'Customer Name' as these are the model's critical fields.
        critical_columns = ['Customer Code', 'Customer Name']
        df.dropna(subset=critical_columns, inplace=True)
        print(f"After dropping rows with missing keys: {len(df)}")
        
        # Step 3: Remove rows where Customer Code is empty string
        df = df[df['Customer Code'].astype(str).str.strip() != '']
        print(f"After removing empty string keys: {len(df)}")
        
        # Step 4: Fill NaNs (User Request)
        # Numeric columns -> 0
        numeric_cols = [
            'Total Target', 'Total Realization', 
            'Target 1-30 Days', 'Target 31-60 Days', 'Target 61 - 90 Days',
            'Target 91 - 120 Days', 'Target 121 - 180 Days', 'Target > 180 Days'
        ]
        # Only fill columns that exist in the dataframe
        existing_numeric_cols = [c for c in numeric_cols if c in df.columns]
        df[existing_numeric_cols] = df[existing_numeric_cols].fillna(0)
        
        # String columns -> ""
        string_cols = ['Customer Name', 'Customer Code', 'Distribution Channel', 'Salesman Name']
        existing_string_cols = [c for c in string_cols if c in df.columns]
        df[existing_string_cols] = df[existing_string_cols].fillna("")
        
        # Step 5: Convert any remaining pandas NaN to None for SQL safety (defensive)
        df = df.where(pd.notnull(df), None)
        
        # Step 6: Reset index
        df.reset_index(drop=True, inplace=True)
        
        print(f"Data cleaning complete: {len(df)} valid rows")
        # ===== END DATA CLEANING =====
        
        # Delete existing records for this report_date (Idempotency)
        db.query(ARAgingReport).filter(ARAgingReport.report_date == report_date).delete()
        db.commit()
        
        # Process each row and build list of records
        debt_records = []
        skipped_rows = 0
        
        for idx, row in df.iterrows():
            # Extract and validate key fields
            customer_name = str(row.get('Customer Name', '')).strip()
            customer_code = str(row.get('Customer Code', '')).strip()
            
            # CRITICAL VALIDATION: Skip rows with empty keys
            if not customer_name or not customer_code:
                print(f"WARNING: Skipping row {idx} - Empty customer_name or customer_code")
                skipped_rows += 1
                continue
            
            # Map channel code to channel name
            channel_code = str(row.get('Distribution Channel', '')).strip()
            channel = CHANNEL_MAP.get(channel_code, 'Others')
            
            # Ensure channel is never None
            if not channel:
                channel = 'Others'
            
            # Create record with validated data
            record = ARAgingReport(
                report_date=report_date,
                salesman_name=str(row.get('Salesman Name', '')).strip(),
                customer_name=customer_name,
                customer_code=customer_code,
                channel=channel,
                total_debt=float(row.get('Total Target', 0)),
                total_realization=float(row.get('Total Realization', 0)),
                debt_1_30=float(row.get('Target 1-30 Days', 0)),
                debt_31_60=float(row.get('Target 31-60 Days', 0)),
                debt_61_90=float(row.get('Target 61 - 90 Days', 0)),
                debt_91_120=float(row.get('Target 91 - 120 Days', 0)),
                debt_121_180=float(row.get('Target 121 - 180 Days', 0)),
                debt_over_180=float(row.get('Target > 180 Days', 0))
            )
            
            debt_records.append(record)
        
        # ===== PRE-INSERT VALIDATION =====
        # Filter empty records (Safety Check)
        debt_records = [r for r in debt_records if r.customer_code]
        print(f"\nPre-insert validation: {len(debt_records)} records to insert")
        
        # Insert records individually and FLUSH to avoid SQLAlchemy sorting issues
        for record in debt_records:
            db.add(record)
            db.flush() 
        
        db.commit()
        
        print(f"Import successful: {len(debt_records)} records imported, {skipped_rows} rows skipped")
        
        return {
            "status": "success",
            "records_imported": len(debt_records),
            "records_skipped": skipped_rows,
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
                "status": "success",
                "report_date": report_date,
                "kpis": {
                    "total_outstanding": 0,
                    "total_collected": 0,
                    "bad_debt": 0,
                    "collection_rate": 0
                },
                "channel_breakdown": [],
                "aging_breakdown": {
                    "1-30 Days": 0,
                    "31-60 Days": 0,
                    "61-90 Days": 0,
                    "91-120 Days": 0,
                    "121-180 Days": 0,
                    ">180 Days": 0
                }
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

def get_available_dates(db: Session) -> List[str]:
    """
    Get distinct available report dates sorted by newest first.
    Excludes future dates (e.g. 9999-12-31) unless that's the only data available.
    """
    try:
        # Primary: Filter out future dates (e.g. 9999-12-31)
        # Using string comparison '2100-01-01' which is safe for standardized date strings
        results = db.query(ARAgingReport.report_date).filter(ARAgingReport.report_date < '2100-01-01').distinct().order_by(ARAgingReport.report_date.desc()).all()
        dates = [r[0] for r in results if r[0]]
        
        # Fallback: If filtered list is empty, return whatever is available (even if it's 9999)
        # This prevents the UI from showing empty dropdowns if only open-items exist
        if not dates:
            fallback = db.query(ARAgingReport.report_date).distinct().order_by(ARAgingReport.report_date.desc()).all()
            dates = [r[0] for r in fallback if r[0]]
            
        return dates
    except Exception as e:
        print(f"Error getting available dates: {e}")
        return []
