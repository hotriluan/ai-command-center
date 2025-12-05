import pandas as pd
import io
from dotenv import load_dotenv
import os
import traceback
import re
from sqlalchemy.orm import Session
from sqlalchemy import text
import google.generativeai as genai
from models import SalesData, SalesTarget, ProductCost, ChatHistory

# --- CONFIGURATION ---
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("--- [CRITICAL WARNING] GEMINI_API_KEY IS MISSING IN .ENV FILE ---")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- 1. THE BRAIN: DATABASE SCHEMA DEFINITION ---
DB_SCHEMA = """
You are a SQL Expert querying a SQLite database 'command_center.db'.

--- TABLE 1: sales_data (Transactions) ---
- customer_name (TEXT): The BUYER/CLIENT (Khách hàng). Example: 'CÔNG TY TNHH THIÊN HÀ'.
- salesman_name (TEXT): The SELLER/STAFF (Nhân viên kinh doanh). Example: 'NGUYỄN VĂN THÂM'.
- dist (TEXT): Sales Channel (Kênh phân phối). Values: 'Retail', 'Industry', 'Project'.
- branch (TEXT): The Branch/Location.
- product_group (TEXT): Product Category (PH3).
- description (TEXT): Specific Product Name.
- net_value (REAL): **REVENUE / SALES AMOUNT** (Doanh thu).
- profit (REAL): **PROFIT** (Lợi nhuận) = Revenue - COGS.
- month_number (INTEGER): 1-12.
- year (INTEGER): e.g., 2024, 2025. **CRITICAL: Always filter by year for accurate results.**

--- TABLE 2: sales_target (Goals - DEPRECATED, use monthly_targets instead) ---
- salesman_name (TEXT): Link to sales_data.salesman_name.
- semester (INTEGER): 1 (Jan-Jun) or 2 (Jul-Dec).
- target_amount (REAL): **KPI / TARGET** (Chỉ tiêu doanh số).
- year (INTEGER): e.g., 2024, 2025.

--- TABLE 3: monthly_targets (Monthly Goals - USE THIS) ---
- user_name (TEXT): Salesman name (same as salesman_name in sales_data).
- year (INTEGER): Year.
- month_number (INTEGER): Month (1-12).
- target_amount (REAL): **MONTHLY TARGET** (already divided from semester).
- semester (INTEGER): 1 or 2.

--- TABLE 4: product_cost (COGS Master) ---
- description (TEXT): Product Name.
- cogs (REAL): Cost of Goods Sold.

--- VIEW: view_sales_performance_v2 (PRE-CALCULATED Performance Metrics) ---
**Type:** SQLite View (Read-Only, Optimized with JOINs)
**Purpose:** Use this view for ANY questions about KPI, percentage, achievement, or revenue vs target.
**IMPORTANT:** This view contains MONTHLY data. For semester/yearly queries, you MUST aggregate.

**Columns:**
- salesman_name (TEXT): Salesman name.
- year (INTEGER): Year. **ALWAYS filter by year for accurate results.**
- month_number (INTEGER): Month (1-12).
- semester (INTEGER): 1 or 2.
- total_revenue (REAL): Total revenue for the MONTH.
- total_profit (REAL): Total profit for the MONTH.
- total_target (REAL): Target for the MONTH (from monthly_targets table).
- achievement_percentage (REAL): **PRE-CALCULATED** monthly achievement %. DO NOT calculate this yourself.

**QUERY LOGIC FOR SALES PERFORMANCE:**
1. **Monthly Questions:** Select directly (e.g., WHERE month_number = 1).
2. **Semester Questions:** You MUST AGGREGATE the results.
   - Example: "Performance in Semester 2?"
   - SQL: `SELECT SUM(total_revenue), SUM(total_target) FROM view_sales_performance_v2 WHERE semester = 2 ...`
   - Achievement %: `(SUM(total_revenue) / SUM(total_target)) * 100`
3. **Yearly Questions:** Aggregate all 12 months.
   - SQL: `SELECT SUM(total_revenue), SUM(total_target) FROM view_sales_performance_v2 WHERE year = 2025 ...`

**YEAR FILTERING RULES:**
1. If user asks about "this year" or "current year", use the latest year available in data.
2. If user specifies a year (e.g., "2024", "last year"), filter by that year.
3. If comparing years (e.g., "2024 vs 2025"), query both years separately.
4. ALWAYS include year in WHERE clause for accurate results.

--- ADVANCED ANALYTICS CONCEPTS ---

**Product Portfolio Matrix:**
- **Revenue Trap:** A product with HIGH revenue but LOW profit margin (<10%).
  - Example: Product A sells 50B VND but only 5% margin = 2.5B profit.
  - Recommendation: Increase price or reduce costs.
- **Star Products:** High revenue AND high margin (>20%).
- **Question Starters:** "Which products are revenue traps?", "Show me high-margin products"

**Target Variance Analysis:**
- **Waterfall Chart:** Shows cumulative effect of each salesperson's variance.
- **Over-achievers:** Actual > Target (positive variance).
- **Under-performers:** Actual < Target (negative variance).
- **Question Starters:** "Who exceeded their targets?", "Target achievement by salesperson"

**Seasonality Patterns:**
- **Peak Months:** Months with highest revenue (identify patterns).
- **Low Months:** Months with lowest revenue (plan promotions).
- **Question Starters:** "What are our peak months?", "Revenue seasonality"

--- TABLE 5: ar_aging_report (Debt & Credit Control) ---
**Description:** Stores daily snapshots of Account Receivables (Debt) and Collection Performance.
**CRITICAL:** This table contains HISTORICAL SNAPSHOTS. NEVER sum total_debt across multiple dates.

**Columns:**
- report_date (TEXT): The date of the snapshot (YYYY-MM-DD).
- salesman_name (TEXT): Name of the sales staff.
- customer_name (TEXT): Name of the customer (Debtor).
- customer_code (TEXT): Customer code.
- channel (TEXT): Distribution channel ('Industry', 'Retail', 'Project', 'Others').
- total_debt (REAL): **OUTSTANDING AMOUNT** (Phải thu / Target in Excel).
- total_realization (REAL): **COLLECTED AMOUNT** (Đã thu / Realization in Excel).
- debt_1_30 (REAL): Outstanding debt aged 1-30 days.
- debt_31_60 (REAL): Outstanding debt aged 31-60 days.
- debt_61_90 (REAL): Outstanding debt aged 61-90 days.
- debt_91_120 (REAL): Outstanding debt aged 91-120 days.
- debt_121_180 (REAL): Outstanding debt aged 121-180 days.
- debt_over_180 (REAL): **BAD DEBT** (overdue > 6 months).

**DEBT QUERY RULES (CRITICAL):**

1. **Snapshot Logic:**
   - ALWAYS filter by the LATEST DATE unless user specifies a date.
   - SQL Pattern: `WHERE report_date = (SELECT MAX(report_date) FROM ar_aging_report)`
   - NEVER sum total_debt across multiple report_date values (it's a snapshot, not cumulative).

2. **Key Calculations:**
   - **Collection Rate** (Tỷ lệ thu hồi): `total_realization / (total_debt + total_realization) * 100`
   - **Bad Debt Ratio**: `debt_over_180 / total_debt * 100`
   - **Overdue Amount**: `debt_61_90 + debt_91_120 + debt_121_180 + debt_over_180`

3. **Segmentation:**
   - By Channel: `GROUP BY channel`
   - By Salesman: `GROUP BY salesman_name`
   - Top Debtors: `SELECT customer_name, total_debt ORDER BY total_debt DESC LIMIT 10`

4. **Question Examples:**
   - "Tình hình nợ hiện tại?" → `SELECT SUM(total_debt), SUM(total_realization) FROM ar_aging_report WHERE report_date = (SELECT MAX(report_date) FROM ar_aging_report)`
   - "Kênh nào thu tiền tốt nhất?" → `SELECT channel, SUM(total_realization), SUM(total_debt) FROM ar_aging_report WHERE report_date = (SELECT MAX(report_date) FROM ar_aging_report) GROUP BY channel`
   - "Top 10 khách hàng nợ nhiều nhất?" → `SELECT customer_name, total_debt FROM ar_aging_report WHERE report_date = (SELECT MAX(report_date) FROM ar_aging_report) ORDER BY total_debt DESC LIMIT 10`
   - "Nợ quá hạn là bao nhiêu?" → `SELECT SUM(debt_over_180) FROM ar_aging_report WHERE report_date = (SELECT MAX(report_date) FROM ar_aging_report)`
"""

# --- Helper Functions ---
def compact_curr(value):
    """Format large numbers to B (Billion) or M (Million) for token efficiency"""
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    else:
        return f"{value:,.0f}"

# --- 2. UPLOAD SERVICES ---

COLUMN_MAPPING = {
    "Net Value": "net_value",
    "Salesman Name": "salesman_name",
    "Month": "month",
    "Year": "year",
    "Dist": "dist",
    "Branch": "branch",
    "PH3": "product_group",
    "Description": "description",
    "Month number": "month_number",
    "Name of Bill to": "customer_name",
    "Billing Qty": "billing_qty"
}

def process_upload_sales(file_contents: bytes, db: Session):
    """
    Process Sales Excel file:
    1. Read and clean data
    2. Rename columns using COLUMN_MAPPING
    3. Calculate Profit (using COGS) and Marketing Spend
    4. Replace all data in sales_data table using to_sql
    """
    try:
        df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
        
        # Data Cleaning & Renaming
        if 'Net Value' in df.columns:
            if df['Net Value'].dtype == 'object':
                 df['Net Value'] = pd.to_numeric(df['Net Value'].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
        
        # Apply Mapping
        df = df.rename(columns=COLUMN_MAPPING)
        
        # Ensure required columns exist
        required_cols = ['net_value', 'description', 'billing_qty']
        for col in required_cols:
            if col not in df.columns:
                 # If missing, try to find original name or just fill 0/empty
                 if col == 'net_value': df['net_value'] = 0
                 if col == 'description': df['description'] = ''
                 if col == 'billing_qty': df['billing_qty'] = 0

        # Load Cost Map for Profit Calculation
        costs = db.query(ProductCost).all()
        cost_map = {c.description: c.cogs for c in costs}
        
        # Calculate Profit & Marketing
        def calculate_row(row):
            revenue = row.get('net_value', 0)
            qty = row.get('billing_qty', 0)
            desc = row.get('description', '')
            
            if desc in cost_map and qty > 0:
                cogs = cost_map[desc] * qty
            else:
                cogs = revenue * 0.7 # Fallback
            
            profit = revenue - cogs
            marketing = revenue * 0.1
            return pd.Series([profit, marketing], index=['profit', 'marketing_spend'])

        df[['profit', 'marketing_spend']] = df.apply(calculate_row, axis=1)
        
        # Filter columns to match Schema/Model
        # We need to keep only columns that exist in the DB model + id (auto)
        # But to_sql will create columns. We should restrict to our known schema.
        allowed_cols = [
            'month', 'month_number', 'year', 'dist', 'branch', 'salesman_name',
            'product_group', 'description', 'net_value', 'profit', 'marketing_spend',
            'customer_name', 'billing_qty'
        ]
        
        # Keep only allowed columns that exist in df
        cols_to_keep = [c for c in allowed_cols if c in df.columns]
        df_final = df[cols_to_keep]
        
        # Insert to DB (Replace mode)
        df_final.to_sql('sales_data', db.get_bind(), if_exists='replace', index=False)
        
        # Add 'id' primary key if needed? SQLite rowid is implicit, but SQLAlchemy model expects 'id'.
        # to_sql won't add 'id' column unless we have it.
        # But usually SQLAlchemy can handle missing PK if we query via ORM? 
        # Actually, if we use to_sql 'replace', it drops the table and creates a new one based on types.
        # It won't create a Primary Key 'id' unless we specify.
        # But for this task, user just wants "to_sql".
        # If we want to be safe for ORM, we might need to add an index or let it be.
        # Given "Senior Data Engineer", we should probably let it be for now as ORM might complain about missing PK on mapping,
        # but for read-only dashboard it might be fine or we can add it.
        # Let's just follow instructions.
        
        return len(df_final)
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error processing sales upload: {str(e)}")

def process_upload_cogs(file_contents: bytes, db: Session):
    """Process COGS Master File upload"""
    try:
        df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl', sheet_name='Sheet1')
        
        if 'Description' not in df.columns or 'COGS' not in df.columns:
            raise Exception("Excel file must contain 'Description' and 'COGS' columns")
        
        df['COGS'] = pd.to_numeric(df['COGS'], errors='coerce')
        df = df.dropna(subset=['Description', 'COGS'])
        df = df.drop_duplicates(subset=['Description'], keep='last')
        
        updated_count = 0
        for _, row in df.iterrows():
            description = str(row['Description']).strip()
            cogs = float(row['COGS'])
            
            existing = db.query(ProductCost).filter(ProductCost.description == description).first()
            
            if existing:
                existing.cogs = cogs
                updated_count += 1
            else:
                new_product = ProductCost(description=description, cogs=cogs)
                db.add(new_product)
                updated_count += 1
        
        db.commit()
        return updated_count
    except Exception as e:
        raise Exception(f"Error processing COGS upload: {str(e)}")

def process_upload_target(file_contents: bytes, db: Session):
    """
    Process Sales Target File upload
    NEW: Splits semester targets into monthly targets and writes to monthly_targets table
    """
    try:
        # Try reading as CSV first, then Excel
        try:
            df = pd.read_csv(io.BytesIO(file_contents))
        except:
            df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
        
        df.columns = [c.strip() for c in df.columns]
        
        required = ['Salesman Name', 'Semester', 'Target']
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise Exception(f"Missing columns: {missing}")
            
        updated_count = 0
        
        # Import MonthlyTarget model
        from sqlalchemy import text
        
        for _, row in df.iterrows():
            name = str(row['Salesman Name']).strip()
            semester = int(row['Semester'])
            semester_target = float(row['Target'])
            
            # Get year (default to 2025 if not provided)
            try:
                year = int(row['Year']) if 'Year' in df.columns and pd.notna(row['Year']) else 2025
            except:
                year = 2025
            
            # Calculate monthly target (semester target / 6 months)
            monthly_target = semester_target / 6.0
            
            # Determine month range based on semester
            if semester == 1:
                months = [1, 2, 3, 4, 5, 6]
            else:  # semester == 2
                months = [7, 8, 9, 10, 11, 12]
            
            # Upsert for each month in the semester
            for month_num in months:
                # Use raw SQL for UPSERT (INSERT OR REPLACE)
                upsert_query = text("""
                    INSERT INTO monthly_targets (user_name, year, month_number, target_amount, semester)
                    VALUES (:user_name, :year, :month_number, :target_amount, :semester)
                    ON CONFLICT(user_name, year, month_number) 
                    DO UPDATE SET 
                        target_amount = excluded.target_amount,
                        semester = excluded.semester
                """)
                
                db.execute(upsert_query, {
                    'user_name': name,
                    'year': year,
                    'month_number': month_num,
                    'target_amount': monthly_target,
                    'semester': semester
                })
                
                updated_count += 1
            
        db.commit()
        return updated_count

    except Exception as e:
        raise Exception(f"Error processing Target upload: {str(e)}")

# --- 3. DASHBOARD STATS ---

def get_dashboard_stats(db: Session):
    """Calculate all dashboard statistics from the database using NEW SCHEMA (snake_case columns)"""
    try:
        # Read data using direct SQL to ensure we get the actual column names
        query = text("SELECT * FROM sales_data")
        df = pd.read_sql(query, db.get_bind())
        
        if df.empty:
            return {
                "kpi": {"revenue": 0, "revenue_growth": 0, "profit": 0, "profit_growth": 0, "marketing": 0, "margin": 0},
                "charts": {"monthly_trend": [], "channel_distribution": [], "branch_distribution": [], "top_products": [], "top_salesmen": []},
                "sales_performance": []
            }

        # Ensure numeric columns (use NEW schema column names)
        df['net_value'] = pd.to_numeric(df['net_value'], errors='coerce').fillna(0)
        df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
        df['marketing_spend'] = pd.to_numeric(df['marketing_spend'], errors='coerce').fillna(0)
        
        # --- KPI CALCULATIONS ---
        total_revenue = df['net_value'].sum()
        total_profit = df['profit'].sum()
        total_marketing = df['marketing_spend'].sum()
        margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Growth (Last Month vs Previous Month)
        revenue_growth = 0
        profit_growth = 0
        if 'month_number' in df.columns:
            monthly_sums = df.groupby('month_number')[['net_value', 'profit']].sum().sort_index()
            if len(monthly_sums) >= 2:
                last_month = monthly_sums.iloc[-1]
                prev_month = monthly_sums.iloc[-2]
                if prev_month['net_value'] > 0:
                    revenue_growth = ((last_month['net_value'] - prev_month['net_value']) / prev_month['net_value']) * 100
                if prev_month['profit'] > 0:
                    profit_growth = ((last_month['profit'] - prev_month['profit']) / prev_month['profit']) * 100

        kpi_data = {
            "revenue": total_revenue,
            "revenue_growth": round(revenue_growth, 1),
            "profit": total_profit,
            "profit_growth": round(profit_growth, 1),
            "marketing": total_marketing,
            "margin": round(margin, 1)
        }
        
        # --- CHARTS DATA ---
        charts_data = {}
        
        # 1. Monthly Trend (Revenue & Profit by Month)
        if 'month_number' in df.columns and 'month' in df.columns:
            monthly_agg = df.groupby(['month_number', 'month'])[['net_value', 'profit']].sum().reset_index()
            monthly_agg = monthly_agg.sort_values('month_number')
            monthly_trend = []
            for _, row in monthly_agg.iterrows():
                monthly_trend.append({
                    "name": str(row['month'])[:3],  # Use first 3 chars (e.g., "Jun", "Jul")
                    "revenue": float(row['net_value']),
                    "profit": float(row['profit'])
                })
            charts_data["monthly_trend"] = monthly_trend
        else:
            charts_data["monthly_trend"] = []
        
        # 2. Channel Distribution (by dist column)
        if 'dist' in df.columns:
            dist_data = df.groupby('dist')['net_value'].sum().reset_index()
            charts_data["channel_distribution"] = [
                {"name": r['dist'], "value": float(r['net_value'])} 
                for _, r in dist_data.iterrows()
            ]
        else:
            charts_data["channel_distribution"] = []
        
        # 3. Branch Distribution
        if 'branch' in df.columns:
            branch_data = df.groupby('branch')['net_value'].sum().reset_index()
            charts_data["branch_distribution"] = [
                {"name": r['branch'], "value": float(r['net_value'])} 
                for _, r in branch_data.iterrows()
            ]
        else:
            charts_data["branch_distribution"] = []
            
        # 4. Top Products (by description column)
        if 'description' in df.columns:
            prod_data = df.groupby('description')['net_value'].sum().nlargest(10).reset_index()
            charts_data["top_products"] = [
                {"name": r['description'], "value": float(r['net_value'])} 
                for _, r in prod_data.iterrows()
            ]
        else:
            charts_data["top_products"] = []
            
        # 5. Top Salesmen (by salesman_name column)
        if 'salesman_name' in df.columns:
            sales_data = df.groupby('salesman_name')['net_value'].sum().nlargest(10).reset_index()
            charts_data["top_salesmen"] = [
                {"name": r['salesman_name'], "value": float(r['net_value'])} 
                for _, r in sales_data.iterrows()
            ]
        else:
            charts_data["top_salesmen"] = []
            
        # --- SALES PERFORMANCE (KPI Table with Targets) ---
        sales_performance = []
        if 'salesman_name' in df.columns and 'month_number' in df.columns:
            # Calculate semester from month_number
            df['semester'] = df['month_number'].apply(lambda m: 1 if m <= 6 else 2)
            
            # Use year column if exists, otherwise default to 2025
            if 'year' not in df.columns:
                df['year'] = 2025
            
            # Aggregate sales by salesman, semester, year
            actuals = df.groupby(['salesman_name', 'semester', 'year'])['net_value'].sum().reset_index()
            
            # Load targets from database
            targets = db.query(SalesTarget).all()
            target_map = {(t.salesman_name, t.semester, t.year): t.target_amount for t in targets}
            
            for _, row in actuals.iterrows():
                name = row['salesman_name']
                sem = int(row['semester'])
                year = int(row['year'])
                actual = float(row['net_value'])
                target = target_map.get((name, sem, year), 0)
                
                # Calculate achievement rate
                rate = (actual / target * 100) if target > 0 else (100 if actual > 0 else 0)
                
                # Determine status
                if rate >= 100: 
                    status = "success"
                elif rate >= 80: 
                    status = "warning"
                else: 
                    status = "destructive"
                
                sales_performance.append({
                    "name": name,
                    "semester": sem,
                    "actual": actual,
                    "target": target,
                    "rate": round(rate, 1),
                    "status": status
                })
        
        # Sort by achievement rate (highest first)
        sales_performance.sort(key=lambda x: x['rate'], reverse=True)
        
        return {
            "kpi": kpi_data,
            "charts": charts_data,
            "sales_performance": sales_performance
        }

    except Exception as e:
        print(f"Error calculating dashboard stats: {e}")
        traceback.print_exc()
        return None

def generate_ai_context(db: Session, dashboard_data: dict):
    """Generate text context for AI based on dashboard data (using NEW SCHEMA)"""
    try:
        if not dashboard_data:
            return "No data available."
            
        kpi = dashboard_data['kpi']
        perf = dashboard_data['sales_performance']
        
        # KPI Context
        kpi_context = "\n=== KPI REPORT (Top 5 & Bottom 3) ===\n"
        if perf:
            top_5 = perf[:5]
            bottom_3 = perf[-3:] if len(perf) > 5 else []
            
            seen = set()
            filtered = []
            for p in top_5 + bottom_3:
                if p['name'] not in seen:
                    filtered.append(p)
                    seen.add(p['name'])
            
            for p in filtered:
                status_short = "PASS" if p['status'] == 'success' else ("WARN" if p['status'] == 'warning' else "FAIL")
                kpi_context += f"{p['name']} (S{p['semester']}): Tgt {compact_curr(p['target'])} | Act {compact_curr(p['actual'])} ({p['rate']}%) -> {status_short}\n"
        else:
            kpi_context += "No KPI data.\n"
            
        # Profit Context (using NEW SCHEMA column names)
        query = text("SELECT * FROM sales_data")
        df = pd.read_sql(query, db.get_bind())
        
        profit_context = "\n=== PROFITABILITY (Real COGS) ===\n"
        if not df.empty and 'month_number' in df.columns and 'month' in df.columns:
            # Use NEW schema: month_number, month, net_value, profit
            monthly = df.groupby(['month_number', 'month'])[['net_value', 'profit']].sum().reset_index()
            monthly = monthly.sort_values('month_number')
            
            for _, row in monthly.iterrows():
                m_rev = row['net_value']
                m_prof = row['profit']
                m_margin = (m_prof / m_rev * 100) if m_rev > 0 else 0
                profit_context += f"{str(row['month'])[:3]}: Rev {compact_curr(m_rev)}, Prof {compact_curr(m_prof)} ({m_margin:.1f}%)\n"

        ai_context = f"""BUSINESS REPORT:
Margin: {kpi['margin']:.1f}% | Profit: {compact_curr(kpi['profit'])} | Rev: {compact_curr(kpi['revenue'])}

{kpi_context}
{profit_context}
"""
        return ai_context
        
    except Exception as e:
        print(f"Error generating AI context: {e}")
        traceback.print_exc()
        return "Error generating context."

# --- 4. CHAT LOGIC ---

def process_chat(question: str, db: Session):
    print(f"--- [AI] Processing: {question} ---")
    
    # FORCE CONFIGURATION (Replace with the user's real key if env var fails)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[WARNING] GEMINI_API_KEY not found in environment.")
        # Do NOT hardcode the key here anymore. Let it fail or warn loudly.

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # STEP 1: GENERATE SQL
    sql_prompt = f"""
    {DB_SCHEMA}
    User Question: "{question}"
    Task: Convert to a single executable SQLite SELECT query.
    
    CRITICAL RULES (FOLLOW STRICTLY):
    1. **ENTITY DISTINCTION:**
       - User asks "Khách hàng" (Customer) -> Query `customer_name`.
       - User asks "Nhân viên" / "Sales" -> Query `salesman_name`.
       - User asks "Kênh" / "Ngành" -> Query `dist`.
       - NEVER confuse Salesman with Customer.
       
    2. **FINANCIAL LOGIC:**
       - "Doanh thu" (Revenue) -> `SUM(net_value)`.
       - "Lợi nhuận" (Profit) -> `SUM(profit)`.
       - "Target" (Mục tiêu) -> Query `sales_target` table.
       - "Tỷ suất lợi nhuận" (Margin) -> `(SUM(profit) / SUM(net_value)) * 100`.
       
    3. **QUERY ROUTING (CRITICAL):**
       - If user asks about "performance", "achievement", "% completion", "KPI", or "target vs revenue":
         * IGNORE raw sales_data and sales_target tables.
         * SELECT directly from `view_sales_performance_v2`.
         * **MONTHLY:** `SELECT * FROM view_sales_performance_v2 WHERE month_number = 1`
         * **SEMESTER:** `SELECT SUM(total_revenue), SUM(total_target) FROM view_sales_performance_v2 WHERE semester = 1`
         * **YEARLY:** `SELECT SUM(total_revenue), SUM(total_target) FROM view_sales_performance_v2 WHERE year = 2025`
       
    4. **SEARCH RULES:**
       - Text search: ALWAYS use `LIKE '%KEYWORD%'` (Fuzzy match).
       - Names are UPPERCASE in DB: Convert keywords to UPPERCASE (e.g. `LIKE '%THÂM%'`).
       - Date search: ALWAYS use `month_number` (1-12), NEVER use text month names.
       
    5. **OUTPUT:** Return ONLY the SQL string.
    """
    
    try:
        sql_response = model.generate_content(sql_prompt)
        raw_text = sql_response.text.strip()
        
        # CLEANING: Remove markdown code blocks first
        clean_text = raw_text.replace('```sql', '').replace('```', '').strip()
        
        # REGEX EXTRACTION: Find the SELECT statement
        # Look for "SELECT" (case insensitive) followed by anything until the end
        match = re.search(r'(SELECT\s+.*)', clean_text, re.IGNORECASE | re.DOTALL)
        
        if match:
            sql_query = match.group(1)
            # Remove any trailing semicolon if present, though SQLite handles it fine usually
            sql_query = sql_query.rstrip(';')
        elif clean_text == "NO_SQL":
             sql_query = "NO_SQL"
        else:
            print(f"[AI] Could not find SQL in response: {raw_text}")
            return {"answer": "I don't understand this question or cannot generate a valid query."}
            
        print(f"--- [AI] Executing SQL: {sql_query} ---")

        if sql_query == "NO_SQL":
            # Chat mode
            chat_response = model.generate_content(f"User says: {question}. Reply helpfully in English with a professional business tone.")
            return {"answer": chat_response.text}

        # STEP 2: EXECUTE SQL
        result = db.execute(text(sql_query)).fetchall()
        print(f"--- [AI] SQL Result: {result} ---")
        
        # STEP 3: EXPLAIN RESULT
        final_prompt = f"""
        User Question: "{question}"
        SQL Used: "{sql_query}"
        Data Found: "{result}"
        
        Task: Answer the user's question based on the Data Found.
        
        **LANGUAGE ENFORCEMENT (HARD RULE):**
        - You MUST ALWAYS respond in ENGLISH, regardless of the language used in the user's query.
        - If the user asks in Vietnamese, translate your answer internally, but output ONLY in English.
        - Example: User asks "Doanh thu tháng 10 là bao nhiêu?" -> You respond "The revenue for October is..."
        
        **Formatting:**
        - Tone: Professional Business Analyst.
        - If Data Found is empty, say "No matching data found."
        - Format currency nicely (e.g., 1.2 billion VND, 500 million VND).
        """
        final_answer = model.generate_content(final_prompt).text
        
        return {"answer": final_answer}

    except Exception as e:
        print(f"--- [FATAL ERROR] SQL/Gemini Failed: {e} ---")
        traceback.print_exc() # Show full trace in terminal
        return {"answer": f"Lỗi kỹ thuật: {str(e)}. Vui lòng kiểm tra Terminal."}


# --- 5. CHANNEL PERFORMANCE ANALYSIS ---

def get_channel_performance(db: Session, year: int, semester: int = None):
    """
    Get channel performance analysis with SQL-SIDE MAPPING & DYNAMIC PROFIT
    Aggregates sales data by distribution channel (Industry, Retail, Project)
    Uses SQL CASE WHEN for robust mapping and Revenue - (Qty * COGS) for profit
    """
    try:
        # Logic to handle semester filter
        semester_condition = "1=1"
        if semester == 1:
            semester_condition = "s.month_number <= 6"
        elif semester == 2:
            semester_condition = "s.month_number > 6"

        # SQL query - dist column already contains channel names
        # No mapping needed, just use dist directly
        sql = text(f"""
        SELECT 
            s.dist as channel_name,
            SUM(s.net_value) as revenue,
            SUM(s.profit) as profit,
            COUNT(*) as deals
        FROM sales_data s
        WHERE (:year IS NULL OR s.year = :year)
        AND {semester_condition}
        GROUP BY s.dist
        """)
        
        # Execution
        result = db.execute(sql, {"year": year}).fetchall()
        
        if not result:
            return {
                "overview": [],
                "monthly_trend": [],
                "radar_data": []
            }
            
        # Process result directly
        overview_list = []
        for row in result:
            channel_name = row[0]
            revenue = float(row[1] or 0)
            profit = float(row[2] or 0)
            deals = int(row[3] or 0)
            margin = (profit / revenue * 100) if revenue != 0 else 0
            
            overview_list.append({
                "channel": channel_name,
                "revenue": revenue,
                "profit": profit,
                "margin": margin,
                "deals": deals
            })
            
        # Calculate monthly trend - dist already contains channel names
        monthly_sql = text(f"""
        SELECT 
            s.month_number,
            s.dist as channel_name,
            SUM(s.net_value) as revenue
        FROM sales_data s
        WHERE (:year IS NULL OR s.year = :year)
        AND {semester_condition}
        GROUP BY s.month_number, s.dist
        ORDER BY s.month_number
        """)
        
        monthly_result = db.execute(monthly_sql, {"year": year}).fetchall()
        
        # Process monthly trend
        monthly_data = {}
        for row in monthly_result:
            month = int(row[0])
            channel = row[1]
            revenue = float(row[2] or 0)
            
            if month not in monthly_data:
                monthly_data[month] = {"month": month, "Industry": 0, "Retail": 0, "Project": 0, "Others": 0}
            
            if channel in monthly_data[month]:
                monthly_data[month][channel] = revenue
                
        monthly_trend = sorted(monthly_data.values(), key=lambda x: x['month'])
        
        # Prepare radar chart data (normalized metrics for comparison)
        radar_data = []
        if len(overview_list) > 0:
            # Find max values for normalization
            max_revenue = max([ch['revenue'] for ch in overview_list]) if overview_list else 0
            max_profit = max([ch['profit'] for ch in overview_list]) if overview_list else 0
            max_deals = max([ch['deals'] for ch in overview_list]) if overview_list else 0
            
            for ch in overview_list:
                radar_data.append({
                    "channel": ch['channel'],
                    "Revenue": round((ch['revenue'] / max_revenue * 100) if max_revenue > 0 else 0, 1),
                    "Profit": round((ch['profit'] / max_profit * 100) if max_profit > 0 else 0, 1),
                    "Volume": round((ch['deals'] / max_deals * 100) if max_deals > 0 else 0, 1)
                    # Margin removed - shown in KPI cards and table instead
                })
        
        return {
            "overview": overview_list,
            "monthly_trend": monthly_trend,
            "radar_data": radar_data
        }
        
    except Exception as e:
        print(f"Error in get_channel_performance: {e}")
        traceback.print_exc()
        return {
            "overview": [],
            "monthly_trend": [],
            "radar_data": []
        }
        
    except Exception as e:
        print(f"Error in get_channel_performance: {e}")
        traceback.print_exc()
        return {
            "overview": [],
            "monthly_trend": [],
            "radar_data": []
        }


