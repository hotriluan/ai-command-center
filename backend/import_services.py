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


def import_production_data(file_contents: bytes, db: Session):
    """
    Import production order data from cooispi.xlsx
    
    Args:
        file_contents: Excel file bytes
        db: SQLAlchemy session
        
    Returns:
        dict with status, rows_processed, and message
    """
    try:
        from models import ProductionOrder
        
        print("\n" + "=" * 80)
        print("PRODUCTION DATA IMPORT")
        print("=" * 80)
        
        # STEP 1: Read Excel
        print("\n[STEP 1] Reading Excel file...")
        df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl', header=None)
        
        # The Excel file has no headers, so we assign column names based on position
        # Based on data analysis: columns are in this order
        column_names = [
            'plant',              # Col 0: 1201
            'sales_order_id',     # Col 1: Sales order (can be NaN for MTS)
            'order_id',           # Col 2: Production order number
            'order_type',         # Col 3: 201S or 201O
            'material_code',      # Col 4: Material number
            'basic_start_date',   # Col 5: Basic start date
            'release_date',       # Col 6: Release date (actual)
            'actual_finish_date', # Col 7: Actual finish date
            'material_description', # Col 8: Material description
            'batch_or_location',  # Col 9: Batch or location code
            'batch',              # Col 10: Batch number
            'system_status',      # Col 11: System status codes
            'mrp_controller',     # Col 12: MRP controller (P01, P02, etc.)
            'order_qty',          # Col 13: Order quantity
            'delivered_qty',      # Col 14: Delivered quantity
            'unit',               # Col 15: Unit of measure
            'date_col_16',        # Col 16: Another date field
            'date_col_17'         # Col 17: Another date field
        ]
        
        df.columns = column_names
        print(f"  ✅ Loaded {len(df):,} rows from Excel (no header)")
        
        # STEP 2: Data Cleaning
        print("\n[STEP 2] Cleaning data...")
        
        # Remove rows where order_id is empty (Total rows, etc.)
        df = df[df['order_id'].notna()]
        df = df[df['order_id'] != '']
        print(f"  ✅ After removing empty orders: {len(df):,} rows")
        
        # Clean sales_order_id: Strip leading zeros and handle empty values
        if 'sales_order_id' in df.columns:
            df['sales_order_id'] = df['sales_order_id'].astype(str).str.strip()
            df['sales_order_id'] = df['sales_order_id'].replace(['nan', 'None', ''], None)
            # For MTS orders (201S), sales_order_id might be empty - that's OK
        
        # Parse dates: Convert to YYYY-MM-DD format
        date_columns = ['basic_start_date', 'release_date', 'actual_finish_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                # Count NaT values
                nat_count = df[col].isna().sum()
                if nat_count > 0:
                    print(f"  ⚠️  {col}: {nat_count} invalid dates found (set to NULL)")
        
        # Convert numeric columns
        numeric_columns = ['order_qty', 'delivered_qty']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # STEP 3: Fetch Existing Orders for Comparison
        print("\n[STEP 3] Fetching existing orders for comparison...")
        
        # Extract all order IDs
        incoming_order_ids = [str(row['order_id']).strip() for _, row in df.iterrows()]
        
        # Fetch existing objects
        existing_orders_query = db.query(ProductionOrder).filter(
            ProductionOrder.order_id.in_(incoming_order_ids)
        ).all()
        
        # Map: order_id -> ProductionOrder object
        existing_map = {order.order_id: order for order in existing_orders_query}
        
        print(f"  📊 Total incoming rows: {len(df)}")
        print(f"  📊 Found in DB: {len(existing_map)}")
        
        # STEP 4: Smart Import (Insert / Update / Skip)
        print("\n[STEP 4] Processing: Insert / Update / Skip...")
        
        new_orders_to_insert = []
        updated_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            order_id = str(row['order_id']).strip()
            
            # Prepare data dict
            # Handle potential NaT/NaN
            bs_date = row['basic_start_date'].date() if pd.notna(row['basic_start_date']) else None
            rel_date = row['release_date'].date() if pd.notna(row['release_date']) else None
            af_date = row['actual_finish_date'].date() if pd.notna(row['actual_finish_date']) else None
            
            order_data = {
                'order_id': order_id,
                'plant': str(row['plant']) if pd.notna(row['plant']) else None,
                'order_type': str(row['order_type']) if pd.notna(row['order_type']) else None,
                'material_code': str(row['material_code']) if pd.notna(row['material_code']) else None,
                'material_description': str(row['material_description']) if pd.notna(row['material_description']) else None,
                'sales_order_id': row['sales_order_id'] if pd.notna(row['sales_order_id']) else None,
                'basic_start_date': bs_date,
                'release_date': rel_date,
                'actual_finish_date': af_date,
                'batch': str(row['batch']) if pd.notna(row['batch']) else None,
                'system_status': str(row['system_status']) if pd.notna(row['system_status']) else None,
                'mrp_controller': str(row['mrp_controller']) if pd.notna(row['mrp_controller']) else None,
                'order_qty': float(row['order_qty']) if pd.notna(row['order_qty']) else 0,
                'delivered_qty': float(row['delivered_qty']) if pd.notna(row['delivered_qty']) else 0,
                'unit': str(row['unit']) if pd.notna(row['unit']) else None
            }

            if order_id in existing_map:
                # Check for changes
                existing_obj = existing_map[order_id]
                has_changes = False
                
                # Compare fields
                # Compare fields
                # Normalization helper for robust comparison
                def normalize(val):
                    if val is None: return None
                    s = str(val).strip()
                    if s.endswith('.0'): return s[:-2]
                    return s

                # Check for changes with normalization
                change_log = []
                
                if normalize(existing_obj.plant) != normalize(order_data['plant']): 
                    change_log.append(f"plant: {existing_obj.plant!r} vs {order_data['plant']!r}")
                
                if normalize(existing_obj.order_type) != normalize(order_data['order_type']): 
                    change_log.append(f"order_type: {existing_obj.order_type!r} vs {order_data['order_type']!r}")
                
                if normalize(existing_obj.material_code) != normalize(order_data['material_code']): 
                    change_log.append(f"material_code: {existing_obj.material_code!r} vs {order_data['material_code']!r}")
                
                if normalize(existing_obj.material_description) != normalize(order_data['material_description']): 
                    change_log.append("material_description: diff")
                
                if normalize(existing_obj.sales_order_id) != normalize(order_data['sales_order_id']): 
                     change_log.append(f"sales_order_id: {existing_obj.sales_order_id!r} vs {order_data['sales_order_id']!r}")
                
                # Dates (convert to string for safe comparison)
                if str(existing_obj.basic_start_date) != str(order_data['basic_start_date']): 
                    change_log.append(f"basic_start_date: {existing_obj.basic_start_date!r} vs {order_data['basic_start_date']!r}")
                
                if str(existing_obj.release_date) != str(order_data['release_date']): 
                    change_log.append(f"release_date: {existing_obj.release_date!r} vs {order_data['release_date']!r}")
                
                if str(existing_obj.actual_finish_date) != str(order_data['actual_finish_date']): 
                    change_log.append(f"actual_finish_date: {existing_obj.actual_finish_date!r} vs {order_data['actual_finish_date']!r}")
                
                # Strings
                if normalize(existing_obj.batch) != normalize(order_data['batch']): 
                    change_log.append(f"batch: {existing_obj.batch!r} vs {order_data['batch']!r}")
                
                if normalize(existing_obj.system_status) != normalize(order_data['system_status']): 
                    change_log.append(f"system_status: {existing_obj.system_status!r} vs {order_data['system_status']!r}")
                
                if normalize(existing_obj.mrp_controller) != normalize(order_data['mrp_controller']): 
                    change_log.append(f"mrp_controller: {existing_obj.mrp_controller!r} vs {order_data['mrp_controller']!r}")
                
                if normalize(existing_obj.unit) != normalize(order_data['unit']): 
                    change_log.append(f"unit: {existing_obj.unit!r} vs {order_data['unit']!r}")

                # Floats (use tolerance)
                if abs((existing_obj.order_qty or 0) - (order_data['order_qty'] or 0)) > 0.001: 
                    change_log.append(f"order_qty: {existing_obj.order_qty} vs {order_data['order_qty']}")
                
                if abs((existing_obj.delivered_qty or 0) - (order_data['delivered_qty'] or 0)) > 0.001: 
                    change_log.append(f"delivered_qty: {existing_obj.delivered_qty} vs {order_data['delivered_qty']}")
                
                if change_log:
                    has_changes = True
                    if updated_count < 10: # Log first 10 differences
                        print(f"  ⚠️ DIFF Order {order_id}: {', '.join(change_log)}")

                if has_changes:
                    # Update existing object
                    for key, value in order_data.items():
                        if key != 'order_id': # PK
                            setattr(existing_obj, key, value)
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # Insert new
                new_order = ProductionOrder(**order_data)
                new_orders_to_insert.append(new_order)
        
        # Commit updates
        if updated_count > 0:
            db.flush() 
            
        # Bulk Insert
        if new_orders_to_insert:
            db.add_all(new_orders_to_insert)
        
        db.commit()
        
        inserted_count = len(new_orders_to_insert)
        
        print(f"\n  ✅ Created: {inserted_count}")
        print(f"  🔄 Updated: {updated_count}")
        print(f"  ⏭️ Skipped (Identical): {skipped_count}")
        
        print("\n" + "=" * 80)
        print("PRODUCTION DATA IMPORT COMPLETE")
        print("=" * 80)
        
        return {
            "status": "success",
            "total_rows_in_file": len(df),
            "imported_new": inserted_count,
            "updated_existing": updated_count,
            "skipped_existing": skipped_count,
            "message": f"Processed {len(df)} rows: {inserted_count} created, {updated_count} updated, {skipped_count} skipped."
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        return {
            "status": "error",
            "message": f"Production import failed: {str(e)}"
        }
