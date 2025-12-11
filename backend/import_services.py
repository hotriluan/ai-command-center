"""
Data Import Service Functions - REWRITTEN FOR IDEMPOTENCY
Purpose: Import sales and COGS data with strict deduplication and validation
"""
import pandas as pd
import io
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

def import_sales_data(file_contents: bytes, db: Session):
    """
    Import sales data with IDEMPOTENT guarantee
    Upload 10 times = Data exists only once
    
    Args:
        file_contents: Excel file bytes
        db: SQLAlchemy session
        
    Returns:
        dict with status, message, and optional report_path
    """
    try:
        print("\n" + "=" * 80)
        print("SALES DATA IMPORT - IDEMPOTENT MODE")
        print("=" * 80)
        
        # STEP 1: Read Excel
        print("\n[STEP 1] Reading Excel file...")
        df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
        
        # Column mapping
        column_mapping = {
            "Billing Document": "billing_document",
            "Billing Item": "billing_item",
            "Material": "material_code",
            "Net Value": "net_value",
            "Salesman Name": "salesman_name",
            "Billing Date": "billing_date",
            "Description": "description",
            "Billing Qty": "billing_qty",
            "Dist": "dist",
            "Branch": "branch",
            "PH3": "product_group",
            "Name of Bill to": "customer_name"
        }
        
        df = df.rename(columns=column_mapping)
        print(f"  ✅ Loaded {len(df):,} rows from Excel")
        
        # STEP 2: Data Preparation
        print("\n[STEP 2] Preparing data...")
        
        # Convert billing_date and extract year/month
        if 'billing_date' in df.columns:
            df['billing_date'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            df['year'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.year
            df['month_number'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.month
            df['month'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.strftime('%b')
        
        # Clean net_value
        if 'net_value' in df.columns:
            if df['net_value'].dtype == 'object':
                df['net_value'] = pd.to_numeric(
                    df['net_value'].astype(str).str.replace(r'[^\d.-]', '', regex=True), 
                    errors='coerce'
                )
        
        # STEP 3: Generate Unique Key
        print("\n[STEP 3] Generating unique keys...")
        
        df['_unique_key'] = (
            df['billing_document'].astype(str) + '_' + 
            df['billing_item'].astype(str)
        )
        
        print(f"  ✅ Generated {len(df):,} unique keys")
        
        # STEP 4: Fetch Existing Keys (Anti-Join)
        print("\n[STEP 4] Checking for existing records...")
        
        existing_query = text("""
            SELECT CONCAT(billing_document, '_', billing_item) as unique_key
            FROM sales_data
            WHERE billing_document IS NOT NULL 
            AND billing_item IS NOT NULL
        """)
        
        existing_df = pd.read_sql(existing_query, db.get_bind())
        existing_keys = set(existing_df['unique_key'].tolist()) if not existing_df.empty else set()
        
        print(f"  Database has {len(existing_keys):,} existing records")
        
        # STEP 5: Filter Duplicates
        print("\n[STEP 5] Filtering duplicates...")
        
        new_records = df[~df['_unique_key'].isin(existing_keys)].copy()
        duplicates_count = len(df) - len(new_records)
        
        print(f"  Excel rows: {len(df):,}")
        print(f"  Duplicates (already in DB): {duplicates_count:,}")
        print(f"  New records to import: {len(new_records):,}")
        
        if len(new_records) == 0:
            return {
                "status": "info",
                "message": "No new data to import. All records already exist in the database.",
                "rows_imported": 0,
                "duplicates_skipped": duplicates_count
            }
        
        # STEP 6: COGS Validation (Pre-flight Check)
        print("\n[STEP 6] COGS validation...")
        
        unique_descriptions = new_records['description'].dropna().unique().tolist()
        
        if unique_descriptions:
            from models import ProductCost
            existing_cogs = db.query(ProductCost.description).all()
            existing_descriptions = {record[0] for record in existing_cogs}
            
            missing_descriptions = [d for d in unique_descriptions if d not in existing_descriptions]
            
            if missing_descriptions:
                # Generate missing COGS report
                report_df = pd.DataFrame({
                    'Description': missing_descriptions
                })
                
                report_path = os.path.join(os.path.dirname(__file__), 'missing_cogs_report.xlsx')
                report_df.to_excel(report_path, index=False)
                
                print(f"  ❌ Missing COGS for {len(missing_descriptions)} products")
                print(f"  Report generated: {report_path}")
                
                return {
                    "status": "error",
                    "message": f"Upload Blocked: Found {len(missing_descriptions)} products without COGS. Please check the generated report.",
                    "report_path": report_path,
                    "missing_count": len(missing_descriptions)
                }
            else:
                print(f"  ✅ All products have COGS")
        
        # STEP 7: Calculate Profit & Marketing Spend
        print("\n[STEP 7] Calculating profit and marketing spend...")
        
        from models import ProductCost
        cogs_records = db.query(ProductCost).all()
        cogs_map = {record.description: record.cogs for record in cogs_records}
        
        def calculate_profit(row):
            revenue = row.get('net_value', 0) or 0
            qty = row.get('billing_qty', 0) or 0
            description = row.get('description', '')
            
            if description in cogs_map and qty > 0:
                cogs = cogs_map[description] * qty
            else:
                cogs = revenue * 0.7  # Fallback
            
            profit = revenue - cogs
            marketing = revenue * 0.1
            return pd.Series([profit, marketing], index=['profit', 'marketing_spend'])
        
        new_records[['profit', 'marketing_spend']] = new_records.apply(calculate_profit, axis=1)
        print(f"  ✅ Calculated profit for {len(new_records):,} records")
        
        # STEP 8: Insert Data
        print("\n[STEP 8] Inserting new records...")
        
        # Select only valid columns
        valid_cols = [
            'billing_document', 'billing_item', 'material_code', 'billing_date',
            'month', 'month_number', 'year', 'dist', 'branch', 'salesman_name',
            'product_group', 'description', 'net_value', 'profit', 'marketing_spend',
            'customer_name', 'billing_qty'
        ]
        
        cols_to_insert = [c for c in valid_cols if c in new_records.columns]
        df_final = new_records[cols_to_insert]
        
        # Remove the temporary _unique_key column if it exists
        if '_unique_key' in df_final.columns:
            df_final = df_final.drop(columns=['_unique_key'])
        
        print(f"  Columns to insert: {len(cols_to_insert)}")
        print(f"  Rows to insert: {len(df_final):,}")
        
        # Insert using append mode
        df_final.to_sql('sales_data', db.get_bind(), if_exists='append', index=False)
        
        print(f"  ✅ Successfully inserted {len(df_final):,} records")
        
        print("\n" + "=" * 80)
        print("✅ IMPORT COMPLETED")
        print("=" * 80)
        
        return {
            "status": "success",
            "message": f"Successfully imported {len(df_final):,} new records. Skipped {duplicates_count:,} duplicates.",
            "rows_imported": len(df_final),
            "duplicates_skipped": duplicates_count
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Import failed: {str(e)}"
        }


def import_cogs_data(file_contents: bytes, db: Session):
    """
    Import/Update COGS data from Excel
    Uses same logic as process_upload_cogs in services.py
    
    Args:
        file_contents: Excel file bytes
        db: SQLAlchemy session
        
    Returns:
        dict with status and message
    """
    try:
        # Read Excel
        df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
        
        # Expect columns: Description, COGS
        if 'Description' not in df.columns or 'COGS' not in df.columns:
            return {
                "status": "error",
                "message": "Invalid file format. Expected columns: Description, COGS"
            }
        
        # Clean data
        df = df[['Description', 'COGS']].dropna()
        
        # Import using ORM
        from models import ProductCost
        
        count = 0
        for _, row in df.iterrows():
            description = row['Description']
            cogs = float(row['COGS'])
            
            # Upsert logic
            existing = db.query(ProductCost).filter(ProductCost.description == description).first()
            
            if existing:
                existing.cogs = cogs
            else:
                new_cost = ProductCost(description=description, cogs=cogs)
                db.add(new_cost)
            
            count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully updated COGS for {count} products",
            "rows_processed": count
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"COGS import failed: {str(e)}"
        }
