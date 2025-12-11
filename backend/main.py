from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
# Trigger reload for Clean Architecture
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import services
import year_services
import semester_services
import import_services
import analytics_services
import debt_services
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import init_db, SessionLocal
from models import SalesData, ChatHistory, ProductCost, SalesTarget
import os
from datetime import datetime

# Gemini API Configuration removed (moved to services.py)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
init_db()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global State
DASHBOARD_DATA = {
    "kpi": {
        "revenue": 0,
        "revenue_growth": 0,
        "profit": 0,
        "profit_growth": 0,
        "marketing": 0,
        "margin": 0
    },
    "charts": {
        "monthly_trend": [],
        "channel_distribution": [],
        "branch_distribution": [],
        "top_products": [],
        "top_salesmen": []
    },
    "sales_performance": []
}

AI_CONTEXT = {
    "rich_context": "No data available yet."
}

def refresh_global_state():
    """Helper to refresh global state from DB using services"""
    global DASHBOARD_DATA, AI_CONTEXT
    db = SessionLocal()
    try:
        # Use year-filtered stats with default year
        default_year = year_services.get_default_year(db)
        stats = year_services.get_dashboard_stats_by_year(db, default_year)
        if stats:
            DASHBOARD_DATA = stats
            AI_CONTEXT["rich_context"] = services.generate_ai_context(db, stats)
            print(f"Global state refreshed successfully for year {default_year}.")
        else:
            print("No data found to refresh global state.")
    except Exception as e:
        print(f"Error refreshing global state: {e}")
    finally:
        db.close()

# Load on startup
refresh_global_state()

@app.get("/")
def read_root():
    return {"message": "Hello General Manager"}

@app.get("/api/dashboard")
def get_dashboard(year: int = None, db: Session = Depends(get_db)):
    """Get dashboard data filtered by year"""
    if year:
        data = year_services.get_dashboard_stats_by_year(db, year)
        return data if data else DASHBOARD_DATA
    return DASHBOARD_DATA

@app.get("/api/available-years")
def get_available_years(db: Session = Depends(get_db)):
    """Get list of available years from sales data"""
    years = year_services.get_available_years(db)
    default_year = year_services.get_default_year(db)
    return {
        "years": years,
        "default_year": default_year
    }

@app.get("/api/performance/semester")
def get_semester_performance(year: int = None, db: Session = Depends(get_db)):
    """Get sales performance grouped by semester"""
    if year is None:
        year = year_services.get_default_year(db)
    return semester_services.get_performance_by_semester(db, year)


@app.post("/api/upload-cogs")
async def upload_cogs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        count = services.process_upload_cogs(contents, db)
        # COGS update affects profit, so refresh stats
        refresh_global_state()
        return {
            "status": "success", 
            "message": f"Updated COGS for {count} products",
            "rows_processed": count
        }
    except Exception as e:
        print(f"Error processing COGS upload: {e}")
        return {"error": str(e)}

# --- FORECASTING ENGINE ---
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

@app.get("/api/forecast")
def get_forecast(year: int = None, db: Session = Depends(get_db)):
    """
    Returns monthly sales revenue and profit data.
    Renamed from forecast but now just shows actual monthly trends.
    """
    try:
        # Determine year
        if year is None:
            year = year_services.get_default_year(db)
        
        # Fetch monthly data
        query = text("""
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
        
        result = db.execute(query, {"year": year}).fetchall()
        
        # Format response
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        data = []
        for row in result:
            month_num = int(row[0])
            month_idx = month_num - 1
            
            data.append({
                "name": month_names[month_idx],
                "revenue": float(row[2] or 0),
                "profit": float(row[3] or 0)
            })
        
        return data
        
    except Exception as e:
        print(f"Error in get_forecast: {e}")
        import traceback
        traceback.print_exc()
        return []


@app.post("/api/upload-target")
async def upload_target(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        count = services.process_upload_target(contents, db)
        refresh_global_state()
        return {
            "status": "success",
            "message": f"Updated Targets for {count} records",
            "rows_processed": count
        }
    except Exception as e:
        print(f"Error processing Target upload: {e}")
        return {"error": str(e)}

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
def chat_analyst(request: ChatRequest, db: Session = Depends(get_db)):
    return services.process_chat(request.question, db)

# --- NEW IMPORT ENDPOINTS WITH VALIDATION ---

@app.post("/api/import/sales")
async def import_sales(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import sales data with duplicate detection and COGS validation
    Returns: {status, message, rows_imported} or {status, error, report_path}
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
        
        contents = await file.read()
        result = import_services.import_sales_data(contents, db)
        
        # Refresh dashboard if import successful
        if result["status"] == "success":
            refresh_global_state()
        
        return result
        
    except Exception as e:
        print(f"Error in import_sales: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import/cogs")
async def import_cogs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import/Update COGS data with upsert logic
    Returns: {status, message, rows_updated}
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
        
        contents = await file.read()
        result = import_services.import_cogs_data(contents, db)
        
        # Refresh dashboard if import successful
        if result["status"] == "success":
            refresh_global_state()
        
        return result
        
    except Exception as e:
        print(f"Error in import_cogs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/missing-cogs-report")
async def download_missing_cogs_report():
    """
    Download the missing COGS report if it exists
    """
    report_path = os.path.join(os.path.dirname(__file__), 'missing_cogs_report.xlsx')
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="No missing COGS report found")
    
    return FileResponse(
        path=report_path,
        filename="missing_cogs_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- ANALYTICS ENDPOINTS ---

@app.get("/api/analytics/product-matrix")
def get_product_matrix(year: int = None, semester: int = None, db: Session = Depends(get_db)):
    """
    Product Portfolio Matrix - Bubble Chart
    Returns: Revenue (x), Profit Margin % (y), Quantity (z), Product Name
    Supports semester filtering: None (whole year), 1 (Jan-Jun), 2 (Jul-Dec)
    """
    try:
        data = analytics_services.get_product_matrix(db, year, semester)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error in product-matrix: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/target-waterfall")
def get_target_waterfall(year: int = None, semester: int = None, db: Session = Depends(get_db)):
    """
    Target Variance Waterfall Chart
    Shows how each salesperson contributed to target achievement
    Supports semester filtering: None (whole year), 1 (Jan-Jun), 2 (Jul-Dec)
    """
    try:
        data = analytics_services.get_target_waterfall(db, year, semester)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error in target-waterfall: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/seasonality")
def get_seasonality(year: int = None, semester: int = None, db: Session = Depends(get_db)):
    """
    Seasonality Heatmap
    Returns revenue by Year x Month for pattern analysis
    Supports semester filtering: None (whole year), 1 (Jan-Jun), 2 (Jul-Dec)
    """
    try:
        data = analytics_services.get_seasonality_heatmap(db, year, semester)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error in seasonality: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/channel-performance")
def get_channel_performance(year: int, semester: int = None, db: Session = Depends(get_db)):
    """
    Channel Performance Analysis
    Returns revenue, profit, and margin by distribution channel (Industry, Retail, Project)
    Includes monthly trend data for stacked visualization
    """
    try:
        data = services.get_channel_performance(db, year, semester)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error in channel-performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- DEBT & CREDIT CONTROL ENDPOINTS ---

@app.post("/api/import/debt")
async def import_debt_report(
    file: UploadFile = File(...),
    report_date: str = None,
    db: Session = Depends(get_db)
):
    """
    Import AR Aging Report (ZRFI005.XLSX)
    Implements idempotent delete-insert pattern
    """
    try:
        # Use provided date or current date
        if not report_date:
            report_date = datetime.now().strftime("%Y-%m-%d")
        
        # Read file contents
        contents = await file.read()
        
        # Import data
        result = debt_services.import_debt_data(contents, db, report_date)
        
        return result
    except Exception as e:
        print(f"Error importing debt report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debt/overview")
def get_debt_overview(report_date: str = None, db: Session = Depends(get_db)):
    """
    Get debt overview with KPIs and breakdowns
    Smart date defaulting: Uses latest report_date if not provided
    """
    try:
        data = debt_services.get_debt_overview(db, report_date)
        return data
    except Exception as e:
        print(f"Error in debt overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debt/top-customers")
def get_top_debt_customers(report_date: str = None, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get top customers by outstanding debt
    Smart date defaulting: Uses latest report_date if not provided
    """
    try:
        data = debt_services.get_top_debtors(db, report_date, limit)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error in top customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)