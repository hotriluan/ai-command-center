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
            "Name of Bill to": "customer_name",
            "SO No.": "so_no",
            "SO Date.": "so_date"
        }
        
        df = df.rename(columns=column_mapping)
        print(f"  [OK] Loaded {len(df):,} rows from Excel")
        
        # STEP 2: Data Preparation
        print("\n[STEP 2] Preparing data...")
        
        # Convert billing_date and extract year/month
        if 'billing_date' in df.columns:
            df['billing_date'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            df['year'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.year
            df['month_number'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.month
            df['month'] = pd.to_datetime(df['billing_date'], errors='coerce').dt.strftime('%b')
        
        # Convert so_date
        if 'so_date' in df.columns:
            df['so_date'] = pd.to_datetime(df['so_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            print(f"  [OK] Processed SO Date column")
        
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
        
        # STEP 4: Load COGS Data for Profit Calculation
        print("\n[STEP 4] Loading COGS data for profit calculation...")
        
        from models import SalesData, ProductCost
        
        # Load COGS map with normalized keys (strip whitespace)
        cogs_records = db.query(ProductCost).all()
        cogs_map = {c.description.strip(): c.cogs for c in cogs_records if c and c.description}
        print(f"  Loaded {len(cogs_map):,} COGS records")
        
        # STEP 5: Fetch Existing Records for Comparison
        print("\n[STEP 5] Fetching existing records for comparison...")
        
        existing_records_query = db.query(SalesData).all()
        
        # Map: (billing_document, billing_item) -> SalesData object
        existing_map = {
            f"{rec.billing_document}_{rec.billing_item}": rec 
            for rec in existing_records_query 
            if rec.billing_document and rec.billing_item is not None
        }
        
        # STEP 5: Validate COGS - Check if all products have COGS
        print("\n[STEP 5] Validating COGS coverage...")
        
        # Get unique products from the import file (normalized)
        unique_products = df['description'].dropna().apply(lambda x: x.strip() if isinstance(x, str) else x).unique()
        print(f"  Found {len(unique_products):,} unique products in import file")
        
        # Check which products are missing COGS
        missing_cogs_products = []
        for product in unique_products:
            if product not in cogs_map:
                missing_cogs_products.append(product)
        
        # If any products are missing COGS, stop and generate report
        if missing_cogs_products:
            print(f"\n  ❌ Found {len(missing_cogs_products):,} products without COGS")
            print(f"  Generating missing COGS report...")
            
            # Create Excel report
            import os
            missing_df = pd.DataFrame({
                'Description': sorted(missing_cogs_products),
                'COGS': [''] * len(missing_cogs_products)
            })
            
            report_path = os.path.join(os.path.dirname(__file__), 'missing_cogs_report.xlsx')
            missing_df.to_excel(report_path, index=False, sheet_name='Sheet1')
            
            print(f"  ✅ Report saved: {report_path}")
            print("\n" + "=" * 80)
            print("⚠️  IMPORT STOPPED - MISSING COGS DATA")
            print("=" * 80)
            
            return {
                "status": "error",
                "message": f"Import stopped: {len(missing_cogs_products)} products are missing COGS data. Please download the report, fill in COGS values, and upload the COGS file before importing sales data again.",
                "missing_cogs_count": len(missing_cogs_products),
                "missing_count": len(missing_cogs_products),  # For frontend compatibility
                "report_path": report_path
            }
        
        print(f"  ✅ All products have COGS data")
        
        # STEP 6: Fetch Existing Records for Comparison
        print("\n[STEP 6] Fetching existing records for comparison...")
        
        existing_records_query = db.query(SalesData).all()
        
        # Map: (billing_document, billing_item) -> SalesData object
        existing_map = {
            f"{rec.billing_document}_{rec.billing_item}": rec 
            for rec in existing_records_query 
            if rec.billing_document and rec.billing_item is not None
        }
        
        print(f"  Database has {len(existing_map):,} existing records")
        
        # STEP 7: Smart Import (Insert / Skip)
        print("\n[STEP 7] Processing: Insert / Skip...")
        
        new_records_to_insert = []
        skipped_count = 0
        
        # Iterate over DataFrame
        for _, row in df.iterrows():
            unique_key = str(row['_unique_key'])
            
            # Prepare data dict with NaN handling
            # Map DF columns to Model attributes
            def safe_value(val):
                """Convert NaN to None, keep other values"""
                return None if pd.isna(val) else val
            
            # Calculate profit using COGS (we know all products have COGS now)
            revenue = safe_value(row['net_value']) or 0
            qty = safe_value(row['billing_qty']) or 0
            description = safe_value(row['description'])
            
            # Normalize description for COGS lookup
            if description:
                description = description.strip()
            
            # Calculate profit with COGS
            if description and description in cogs_map and qty > 0:
                cogs_total = cogs_map[description] * qty
                profit = revenue - cogs_total
            else:
                # This shouldn't happen since we validated, but just in case
                profit = 0
            
            record_data = {
                'billing_document': safe_value(row['billing_document']),
                'billing_item': safe_value(row['billing_item']),
                'material_code': safe_value(row['material_code']),
                'net_value': revenue,
                'salesman_name': safe_value(row['salesman_name']),
                'billing_date': safe_value(row['billing_date']),
                'description': description,
                'billing_qty': qty,
                'dist': safe_value(row['dist']),
                'branch': safe_value(row['branch']),
                'product_group': safe_value(row['product_group']),
                'customer_name': safe_value(row['customer_name']),
                'so_no': safe_value(row['so_no']) if 'so_no' in row else None,
                'so_date': safe_value(row['so_date']) if 'so_date' in row else None,
                'year': safe_value(row['year']),
                'month': safe_value(row['month']),
                'month_number': safe_value(row['month_number']),
                # Calculated fields
                'profit': profit,
                'marketing_spend': revenue * 0.1  # 10% of revenue
            }
            
            if unique_key in existing_map:
                # Skip Logic - Record already exists
                skipped_count += 1
            else:
                # Insert Logic - New record
                new_record = SalesData(**record_data)
                new_records_to_insert.append(new_record)
        
        # Bulk insert new
        if new_records_to_insert:
            db.add_all(new_records_to_insert)
            
        db.commit()
        
        print(f"  ✅ Created: {len(new_records_to_insert):,}")
        print(f"  ⏭️  Skipped (already exists): {skipped_count:,}")
        
        print("\n" + "=" * 80)
        print("✅ IMPORT COMPLETED")
        print("=" * 80)
        
        return {
            "status": "success",
            "message": f"Import completed: {len(new_records_to_insert):,} new records created, {skipped_count:,} existing records skipped.",
            "rows_imported": len(new_records_to_insert),
            "rows_skipped": skipped_count
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
            
            # Flush after each record to avoid batch sorting issues with None primary keys
            db.flush()
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



