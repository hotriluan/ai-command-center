"""
System Audit Script for Production Analytics Integration
Checks database, backend, and frontend readiness
"""

import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime

def audit_database():
    """Audit database layer - check sales_data table structure"""
    print("=" * 60)
    print("1. DATABASE LAYER AUDIT")
    print("=" * 60)
    
    db_path = Path("backend/command_center.db")
    
    if not db_path.exists():
        return {
            "status": "ERROR",
            "message": "Database file not found",
            "tables": []
        }
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nFound tables: {', '.join(tables)}")
    
    db_audit = {
        "status": "SUCCESS",
        "tables": tables,
        "sales_data_schema": None,
        "sample_data": None,
        "join_key_candidates": [],
        "date_columns": []
    }
    
    # Focus on sales_data table
    if "sales_data" in tables:
        print("\n✓ sales_data table exists")
        
        # Get schema
        cursor.execute("PRAGMA table_info(sales_data)")
        schema = cursor.fetchall()
        
        db_audit["sales_data_schema"] = [
            {
                "name": col[1],
                "type": col[2],
                "nullable": not col[3],
                "pk": bool(col[5])
            }
            for col in schema
        ]
        
        print("\nTable Structure:")
        print(f"{'Column Name':<30} {'Type':<15} {'Nullable':<10} {'PK'}")
        print("-" * 70)
        for col in db_audit["sales_data_schema"]:
            print(f"{col['name']:<30} {col['type']:<15} {str(col['nullable']):<10} {'✓' if col['pk'] else ''}")
        
        # Identify potential join keys
        join_key_patterns = ['order', 'so', 'sales', 'document', 'number']
        for col in db_audit["sales_data_schema"]:
            col_lower = col['name'].lower()
            if any(pattern in col_lower for pattern in join_key_patterns):
                db_audit["join_key_candidates"].append(col['name'])
        
        # Identify date columns
        for col in db_audit["sales_data_schema"]:
            col_lower = col['name'].lower()
            if 'date' in col_lower or 'time' in col_lower or col['type'].upper() in ['DATE', 'DATETIME', 'TIMESTAMP']:
                db_audit["date_columns"].append({
                    "name": col['name'],
                    "type": col['type']
                })
        
        print(f"\n📌 Potential JOIN KEY candidates: {', '.join(db_audit['join_key_candidates']) if db_audit['join_key_candidates'] else 'NONE FOUND'}")
        print(f"📅 Date columns: {', '.join([d['name'] for d in db_audit['date_columns']]) if db_audit['date_columns'] else 'NONE FOUND'}")
        
        # Get sample data
        cursor.execute("SELECT * FROM sales_data LIMIT 3")
        sample_rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        db_audit["sample_data"] = []
        for row in sample_rows:
            db_audit["sample_data"].append(dict(zip(column_names, row)))
        
        print("\nSample Data (first row):")
        if db_audit["sample_data"]:
            for key, value in list(db_audit["sample_data"][0].items())[:5]:
                print(f"  {key}: {value}")
        
        # Row count
        cursor.execute("SELECT COUNT(*) FROM sales_data")
        count = cursor.fetchone()[0]
        db_audit["row_count"] = count
        print(f"\nTotal rows: {count:,}")
    else:
        print("\n✗ sales_data table NOT FOUND")
    
    conn.close()
    return db_audit

def audit_backend():
    """Audit backend layer - API structure and models"""
    print("\n" + "=" * 60)
    print("2. BACKEND LAYER AUDIT")
    print("=" * 60)
    
    backend_path = Path("backend")
    
    backend_audit = {
        "status": "SUCCESS",
        "files": [],
        "models": [],
        "api_endpoints": [],
        "date_parsing_logic": []
    }
    
    # List key files
    key_files = ['main.py', 'models.py', 'services.py', 'database.py']
    for file in key_files:
        file_path = backend_path / file
        if file_path.exists():
            backend_audit["files"].append(str(file))
            print(f"✓ {file}")
        else:
            print(f"✗ {file} NOT FOUND")
    
    # Check models.py for Pydantic/SQLAlchemy models
    models_path = backend_path / "models.py"
    if models_path.exists():
        content = models_path.read_text(encoding='utf-8')
        
        # Find class definitions
        import re
        classes = re.findall(r'class (\w+)\(.*?\):', content)
        backend_audit["models"] = classes
        print(f"\nFound models: {', '.join(classes)}")
        
        # Check for SalesData model
        if 'SalesData' in classes:
            print("✓ SalesData model exists")
    
    # Check main.py for API endpoints
    main_path = backend_path / "main.py"
    if main_path.exists():
        content = main_path.read_text(encoding='utf-8')
        
        # Find API routes
        routes = re.findall(r'@app\.(get|post|put|delete)\(["\']([^"\']+)', content)
        backend_audit["api_endpoints"] = [{"method": method.upper(), "path": path} for method, path in routes]
        
        print("\nAPI Endpoints:")
        for endpoint in backend_audit["api_endpoints"]:
            print(f"  {endpoint['method']:<6} {endpoint['path']}")
    
    # Check for date parsing logic
    services_path = backend_path / "services.py"
    if services_path.exists():
        content = services_path.read_text(encoding='utf-8')
        
        # Look for date-related imports and functions
        if 'pd.to_datetime' in content:
            backend_audit["date_parsing_logic"].append("Uses pandas.to_datetime")
        if 'datetime' in content:
            backend_audit["date_parsing_logic"].append("Uses Python datetime module")
        
        print(f"\nDate parsing: {', '.join(backend_audit['date_parsing_logic']) if backend_audit['date_parsing_logic'] else 'Not detected'}")
    
    return backend_audit

def audit_frontend():
    """Audit frontend layer - structure and components"""
    print("\n" + "=" * 60)
    print("3. FRONTEND LAYER AUDIT")
    print("=" * 60)
    
    frontend_path = Path("frontend")
    
    frontend_audit = {
        "status": "SUCCESS",
        "structure": {},
        "components": [],
        "pages": [],
        "dashboard_locations": []
    }
    
    if not frontend_path.exists():
        print("✗ frontend directory NOT FOUND")
        frontend_audit["status"] = "ERROR"
        return frontend_audit
    
    # Check key directories
    key_dirs = ['src', 'app', 'components', 'public']
    for dir_name in key_dirs:
        dir_path = frontend_path / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ exists")
            
            # List files in this directory
            files = [f.name for f in dir_path.iterdir() if f.is_file()]
            frontend_audit["structure"][dir_name] = files
            
            if dir_name == 'components':
                frontend_audit["components"] = files
            elif dir_name == 'app':
                frontend_audit["pages"] = files
        else:
            print(f"✗ {dir_name}/ NOT FOUND")
    
    # Look for dashboard/report components
    components_path = frontend_path / "components"
    if components_path.exists():
        for file in components_path.glob("*.tsx"):
            content = file.read_text(encoding='utf-8')
            if any(keyword in content.lower() for keyword in ['dashboard', 'report', 'chart', 'analytics']):
                frontend_audit["dashboard_locations"].append(file.name)
        
        print(f"\nDashboard-related components: {', '.join(frontend_audit['dashboard_locations']) if frontend_audit['dashboard_locations'] else 'None'}")
    
    # Check app routing
    app_path = frontend_path / "app"
    if app_path.exists():
        page_file = app_path / "page.tsx"
        if page_file.exists():
            print(f"\n✓ Main page.tsx exists")
    
    return frontend_audit

def generate_report(db_audit, backend_audit, frontend_audit):
    """Generate markdown report"""
    print("\n" + "=" * 60)
    print("GENERATING REPORT")
    print("=" * 60)
    
    report = f"""# System State Report: Production Analytics Integration Readiness

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This audit assesses the readiness of the AI Command Center system to integrate Production Order data with existing Sales Data.

---

## 1. Database Layer Analysis

### Status: {db_audit['status']}

### Tables Found
{', '.join(db_audit['tables']) if db_audit['tables'] else 'No tables found'}

### Sales Data Schema

"""
    
    if db_audit['sales_data_schema']:
        report += "| Column Name | Type | Nullable | Primary Key |\n"
        report += "|-------------|------|----------|-------------|\n"
        for col in db_audit['sales_data_schema']:
            report += f"| {col['name']} | {col['type']} | {col['nullable']} | {'✓' if col['pk'] else ''} |\n"
        
        report += f"\n**Total Rows:** {db_audit.get('row_count', 'N/A'):,}\n"
    else:
        report += "*sales_data table not found*\n"
    
    report += f"""
### JOIN KEY Identification

**Candidates for linking with Production Orders (`cooispi.xlsx`):**

"""
    
    if db_audit['join_key_candidates']:
        for key in db_audit['join_key_candidates']:
            report += f"- `{key}` - Potential match for `Sales order` field\n"
        
        report += f"""
**Recommendation:** Inspect sample values in these columns to confirm which matches `cooispi['Sales order']` format.
"""
    else:
        report += "⚠️ **WARNING:** No obvious join key found. Manual column mapping required.\n"
    
    report += f"""
### Date Columns

"""
    
    if db_audit['date_columns']:
        for date_col in db_audit['date_columns']:
            report += f"- `{date_col['name']}` ({date_col['type']})\n"
    else:
        report += "⚠️ No date columns detected.\n"
    
    report += f"""

---

## 2. Backend Layer Analysis

### Status: {backend_audit['status']}

### Key Files
"""
    
    for file in backend_audit['files']:
        report += f"- ✓ `{file}`\n"
    
    report += f"""
### Data Models

Found {len(backend_audit['models'])} model(s):
"""
    
    for model in backend_audit['models']:
        report += f"- `{model}`\n"
    
    report += f"""
### API Endpoints

"""
    
    for endpoint in backend_audit['api_endpoints']:
        report += f"- `{endpoint['method']}` {endpoint['path']}\n"
    
    report += f"""
### Date Parsing Logic

"""
    
    if backend_audit['date_parsing_logic']:
        for logic in backend_audit['date_parsing_logic']:
            report += f"- {logic}\n"
    else:
        report += "- No date parsing detected\n"
    
    report += f"""

---

## 3. Frontend Layer Analysis

### Status: {frontend_audit['status']}

### Directory Structure

"""
    
    for dir_name, files in frontend_audit['structure'].items():
        report += f"**{dir_name}/**\n"
        for file in files[:10]:  # Limit to first 10
            report += f"  - {file}\n"
        if len(files) > 10:
            report += f"  - ... and {len(files) - 10} more\n"
    
    report += f"""
### Dashboard Components

"""
    
    if frontend_audit['dashboard_locations']:
        for comp in frontend_audit['dashboard_locations']:
            report += f"- `{comp}`\n"
    else:
        report += "- No dashboard components detected\n"
    
    report += """

---

## 4. Gap Analysis for Production Analytics

### What's Missing

#### Database Layer
"""
    
    if not db_audit.get('join_key_candidates'):
        report += "1. ❌ **No clear JOIN KEY** between sales_data and future production_orders table\n"
    else:
        report += "1. ✓ Potential join keys identified\n"
    
    report += """
2. ❌ **Missing Table:** `production_orders` - Need to create new table for `cooispi.xlsx` data
3. ❌ **Missing Columns:** Lead time calculation requires:
   - Production Order Date
   - Production Completion Date
   - Sales Order Number (for join)

#### Backend Layer

1. ❌ **Missing Model:** Need `ProductionOrder` SQLAlchemy model
2. ❌ **Missing API Endpoint:** `/api/production/lead-time-analysis`
3. ❌ **Missing Service:** Lead time calculation logic (date difference between SO and Production dates)

#### Frontend Layer

1. ❌ **Missing Component:** ProductionAnalyticsDashboard.tsx
2. ❌ **Missing Chart:** Lead Time Trend Chart
3. ❌ **Missing Integration:** Menu item for Production Analytics

---

## 5. Recommended Next Steps

### Phase 1: Data Import (Week 1)
1. Create `production_orders` table with proper schema
2. Build import service for `cooispi.xlsx` (similar to existing sales import)
3. Establish JOIN relationship between tables

### Phase 2: Backend API (Week 1-2)
1. Create `ProductionOrder` model in models.py
2. Add endpoint: `POST /api/upload-production` for file upload
3. Add endpoint: `GET /api/production/lead-time` for analytics
4. Implement date difference calculation (SO Date → Production Date)

### Phase 3: Frontend Dashboard (Week 2)
1. Create `ProductionDashboard.tsx` component
2. Add lead time trend chart (line/bar chart)
3. Add filters: Date range, Sales Order, Product
4. Integrate into main navigation

### Phase 4: Testing & Validation (Week 3)
1. Test data import with actual `cooispi.xlsx`
2. Validate join accuracy
3. QA dashboard visualizations

---

## 6. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| JOIN key mismatch | HIGH | Validate sample data before full import |
| Date format inconsistency | MEDIUM | Standardize date parsing with pd.to_datetime |
| Performance with large datasets | MEDIUM | Add database indexing on join columns |
| Missing production data | LOW | Implement proper error handling |

---

## Conclusion

The system has a **solid foundation** (existing sales data pipeline) but requires **3 new components**:
1. Production Orders table
2. Lead Time API
3. Production Dashboard UI

**Estimated effort:** 2-3 weeks for full integration.

**Next Action:** Review this report with stakeholders and prioritize Phase 1 (Data Import).
"""
    
    # Write report
    report_path = Path("system_state_report.md")
    report_path.write_text(report, encoding='utf-8')
    print(f"\n✓ Report generated: {report_path.absolute()}")
    
    return report

def main():
    print("🔍 AI COMMAND CENTER - SYSTEM AUDIT")
    print("=" * 60)
    print("Purpose: Assess readiness for Production Analytics Integration")
    print("=" * 60)
    
    # Run audits
    db_audit = audit_database()
    backend_audit = audit_backend()
    frontend_audit = audit_frontend()
    
    # Generate report
    report = generate_report(db_audit, backend_audit, frontend_audit)
    
    print("\n" + "=" * 60)
    print("✓ AUDIT COMPLETE")
    print("=" * 60)
    print("\nReview system_state_report.md for detailed findings.")

if __name__ == "__main__":
    main()
