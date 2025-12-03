from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import json
import pandas as pd
import io
from sqlalchemy.orm import Session
from database import init_db, SessionLocal, SalesData, ChatHistory

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyC-hEpkyCVzKt6fXNMCMLjxtM139DN87Qk"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

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
    }
}

AI_CONTEXT = {
    "rich_context": "No data available yet."
}

def process_dataframe(df):
    """Core logic to update DASHBOARD_DATA and AI_CONTEXT from a DataFrame"""
    global DASHBOARD_DATA, AI_CONTEXT
    
    if df.empty:
        return

    # 1. Aggregation for Dashboard
    # Ensure columns exist
    required_cols = ['Year', 'Month_Num', 'Month_Label', 'Revenue']
    for col in required_cols:
        if col not in df.columns:
            pass

    # --- KPI Calculation ---
    total_revenue = df['Revenue'].sum()
    total_profit = total_revenue * 0.30
    total_marketing = total_revenue * 0.10
    margin = 30.0
    
    # Simple growth calculation (Last Month vs Previous Month) if possible
    revenue_growth = 0
    profit_growth = 0
    
    if 'Month_Num' in df.columns:
        monthly_sums = df.groupby('Month_Num')['Revenue'].sum().sort_index()
        if len(monthly_sums) >= 2:
            last_month = monthly_sums.iloc[-1]
            prev_month = monthly_sums.iloc[-2]
            if prev_month > 0:
                revenue_growth = ((last_month - prev_month) / prev_month) * 100
                profit_growth = revenue_growth # Assuming constant margin
    
    DASHBOARD_DATA["kpi"] = {
        "revenue": total_revenue,
        "revenue_growth": round(revenue_growth, 1),
        "profit": total_profit,
        "profit_growth": round(profit_growth, 1),
        "marketing": total_marketing,
        "margin": margin
    }

    # --- Charts Generation ---
    
    # 1. Monthly Trend
    monthly_agg = df.groupby(['Year', 'Month_Num', 'Month_Label'])['Revenue'].sum().reset_index()
    monthly_agg = monthly_agg.sort_values(['Year', 'Month_Num'])
    
    monthly_trend = []
    for _, row in monthly_agg.iterrows():
        rev = float(row['Revenue'])
        month_short = str(row['Month_Label'])[:3]
        monthly_trend.append({
            "name": month_short,
            "revenue": rev,
            "profit": rev * 0.30
        })
    DASHBOARD_DATA["charts"]["monthly_trend"] = monthly_trend

    # 2. Channel Distribution
    if 'Dist' in df.columns:
        dist_data = df.groupby('Dist')['Revenue'].sum().reset_index()
        DASHBOARD_DATA["charts"]["channel_distribution"] = [
            {"name": row['Dist'], "value": float(row['Revenue'])} 
            for _, row in dist_data.iterrows()
        ]

    # 3. Branch Distribution
    if 'Branch' in df.columns:
        branch_data = df.groupby('Branch')['Revenue'].sum().reset_index()
        DASHBOARD_DATA["charts"]["branch_distribution"] = [
            {"name": row['Branch'], "value": float(row['Revenue'])}
            for _, row in branch_data.iterrows()
        ]

    # 4. Top Products (Top 5)
    if 'Description' in df.columns:
        prod_data = df.groupby('Description')['Revenue'].sum().nlargest(5).reset_index()
        DASHBOARD_DATA["charts"]["top_products"] = [
            {"name": row['Description'], "value": float(row['Revenue'])}
            for _, row in prod_data.iterrows()
        ]

    # 5. Top Salesmen (Top 5)
    if 'Salesman Name' in df.columns:
        sales_data = df.groupby('Salesman Name')['Revenue'].sum().nlargest(5).reset_index()
        DASHBOARD_DATA["charts"]["top_salesmen"] = [
            {"name": row['Salesman Name'], "value": float(row['Revenue'])}
            for _, row in sales_data.iterrows()
        ]

    # 2. Generate AI Context
    ai_context = "DETAILED MONTHLY BUSINESS BREAKDOWN:\n\n"
    def fmt_vnd(val):
        return f"{val:,.0f}"

    if 'Month_Num' in df.columns and 'Month_Label' in df.columns:
        month_map = df[['Month_Num', 'Month_Label']].drop_duplicates().sort_values('Month_Num')
        
        for _, m_row in month_map.iterrows():
            m_num = m_row['Month_Num']
            m_label = m_row['Month_Label']
            
            monthly_data = df[df['Month_Num'] == m_num]
            monthly_total = monthly_data['Revenue'].sum()
            
            ai_context += f"=== REPORT FOR {m_label} (Total: {fmt_vnd(monthly_total)} VND) ===\n"
            
            # Salesman
            if 'Salesman Name' in df.columns:
                salesman_stats = monthly_data.groupby('Salesman Name')['Revenue'].sum().sort_values(ascending=False)
                ai_context += "  > Salesmen Performance:\n"
                for name, val in salesman_stats.items():
                    ai_context += f"    - {name}: {fmt_vnd(val)}\n"

            # Branch & Channel
            if 'Branch' in df.columns:
                branch_stats = monthly_data.groupby('Branch')['Revenue'].sum().to_dict()
                branch_str = ", ".join([f"{k}: {fmt_vnd(v)}" for k,v in branch_stats.items()])
                ai_context += f"  > Branches: {branch_str}\n"
            
            if 'Dist' in df.columns: # DB column might be dist_channel
                dist_stats = monthly_data.groupby('Dist')['Revenue'].sum().to_dict()
                dist_str = ", ".join([f"{k}: {fmt_vnd(v)}" for k,v in dist_stats.items()])
                ai_context += f"  > Channels: {dist_str}\n"

            # Top Products
            if 'Description' in df.columns: # DB column product_desc
                prod_stats = monthly_data.groupby('Description')['Revenue'].sum().nlargest(20)
                ai_context += "  > Top 20 Products:\n"
                for name, val in prod_stats.items():
                    ai_context += f"    - {name}: {fmt_vnd(val)}\n"

            # Top Customers
            if 'Name of Bill to' in df.columns: # DB column customer_name
                cust_stats = monthly_data.groupby('Name of Bill to')['Revenue'].sum().nlargest(10)
                ai_context += "  > Top 10 Customers:\n"
                for name, val in cust_stats.items():
                    ai_context += f"    - {name}: {fmt_vnd(val)}\n"
            
            ai_context += "\n"
    
    AI_CONTEXT["rich_context"] = ai_context
    print("Context updated successfully.")

def load_context_from_db():
    """Load data from SQLite and rebuild context"""
    db = SessionLocal()
    try:
        # Read all data
        query = db.query(SalesData)
        df = pd.read_sql(query.statement, db.bind)
        
        if not df.empty:
            # Map DB columns back to DF columns expected by logic
            # DB: year, month_num, month_label, dist_channel, branch, salesman_name, product_group, product_desc, customer_name, revenue
            # Logic expects: Year, Month_Num, Month_Label, Dist, Branch, Salesman Name, PH3, Description, Name of Bill to, Revenue
            
            df = df.rename(columns={
                'year': 'Year',
                'month_num': 'Month_Num',
                'month_label': 'Month_Label',
                'dist_channel': 'Dist',
                'branch': 'Branch',
                'salesman_name': 'Salesman Name',
                'product_group': 'PH3',
                'product_desc': 'Description',
                'customer_name': 'Name of Bill to',
                'revenue': 'Revenue'
            })
            
            print(f"Loaded {len(df)} rows from database.")
            process_dataframe(df)
        else:
            print("Database is empty.")
            
    except Exception as e:
        print(f"Error loading from DB: {e}")
    finally:
        db.close()

# Load on startup
load_context_from_db()

@app.get("/")
def read_root():
    return {"message": "Hello General Manager"}

@app.get("/api/dashboard")
def get_dashboard():
    return DASHBOARD_DATA

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        
        # Data Cleaning
        if df['Net Value'].dtype == 'object':
             df['Net Value'] = pd.to_numeric(df['Net Value'].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
        df = df.rename(columns={'Net Value': 'Revenue'})
        
        if 'Month number' in df.columns:
            df['Month_Num'] = pd.to_numeric(df['Month number'], errors='coerce').fillna(0).astype(int)
        else:
            df['Month_Num'] = 0
            
        if 'Month' in df.columns:
            df['Month_Label'] = df['Month'].astype(str)
        else:
            df['Month_Label'] = "Unknown"

        # Wipe old data
        db.query(SalesData).delete()
        db.commit()
        
        # Insert new data
        # Map DF columns to DB model
        sales_objects = []
        for _, row in df.iterrows():
            obj = SalesData(
                year=row.get('Year'),
                month_num=row.get('Month_Num'),
                month_label=row.get('Month_Label'),
                dist_channel=row.get('Dist'),
                branch=row.get('Branch'),
                salesman_name=row.get('Salesman Name'),
                product_group=row.get('PH3'),
                product_desc=row.get('Description'),
                customer_name=row.get('Name of Bill to'),
                revenue=row.get('Revenue')
            )
            sales_objects.append(obj)
        
        db.add_all(sales_objects)
        db.commit()
        
        # Refresh Context (using the DF we just processed to save a read, or just call load_context_from_db)
        # Calling load_context_from_db ensures we test the read path too
        load_context_from_db()
        
        return {"status": "success", "rows_processed": len(df)}

    except Exception as e:
        print(f"Error processing upload: {e}")
        return {"error": str(e)}

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
def chat_analyst(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Save User Question
        user_msg = ChatHistory(role='user', content=request.question)
        db.add(user_msg)
        db.commit()

        prompt = f"""You are a helpful Business Intelligence Analyst for 'NextGen Trading'. 
Here is the current business data in JSON format:
{json.dumps(DASHBOARD_DATA, indent=2)}

DEEP DIVE CONTEXT from latest data upload:
{AI_CONTEXT.get("rich_context", "No detailed context available.")}

User Question: {request.question}

Analyze the data and answer briefly and professionally. Focus on insights and trends.
Use the DEEP DIVE CONTEXT to answer specific questions about Channels, Branches, Products, or Salesmen.
Always quote values in VND (Vietnam Dong)."""

        response = model.generate_content(prompt)
        answer_text = response.text
        
        # Save AI Answer
        ai_msg = ChatHistory(role='ai', content=answer_text)
        db.add(ai_msg)
        db.commit()
        
        return {"answer": answer_text}
    
    except Exception as e:
        return {"answer": "AI Service is currently unavailable. Please check API Key."}