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
        stats = services.get_dashboard_stats(db)
        if stats:
            DASHBOARD_DATA = stats
            AI_CONTEXT["rich_context"] = services.generate_ai_context(db, stats)
            print("Global state refreshed successfully.")
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