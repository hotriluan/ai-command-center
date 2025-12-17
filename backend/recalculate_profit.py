"""
Recalculate profit for all sales_data records using COGS
Formula: Profit = Revenue - (Quantity × COGS)
Fallback: If no COGS found, use Profit = Revenue × 0.3 (30% margin estimate)
"""
from database import SessionLocal
from sqlalchemy import text
import time

db = SessionLocal()

try:
    print("\n" + "=" * 80)
    print("RECALCULATING PROFIT FOR ALL SALES RECORDS")
    print("=" * 80)
    
    # Step 1: Get COGS data into memory
    print("\n[STEP 1] Loading COGS data...")
    cogs_query = text("SELECT description, cogs FROM product_cost")
    cogs_result = db.execute(cogs_query).fetchall()
    
    cogs_map = {row[0]: float(row[1]) for row in cogs_result}
    print(f"  ✅ Loaded {len(cogs_map):,} COGS records")
    
    # Step 2: Update profit for all records
    print("\n[STEP 2] Recalculating profit...")
    print("  This may take a few minutes for 77,864 records...")
    
    # Use a single UPDATE with CASE WHEN for better performance
    # But MySQL doesn't support hash maps, so we'll do batch updates
    
    # Get all unique products from sales_data
    products_query = text("""
        SELECT DISTINCT description 
        FROM sales_data 
        WHERE description IS NOT NULL
    """)
    products = db.execute(products_query).fetchall()
    
    print(f"  Found {len(products):,} unique products in sales data")
    
    updated_count = 0
    matched_count = 0
    fallback_count = 0
    
    start_time = time.time()
    
    for i, (product,) in enumerate(products, 1):
        if product in cogs_map:
            # Update with actual COGS
            cogs_value = cogs_map[product]
            update_sql = text("""
                UPDATE sales_data
                SET profit = net_value - (billing_qty * :cogs)
                WHERE description = :product
            """)
            result = db.execute(update_sql, {"cogs": cogs_value, "product": product})
            updated_count += result.rowcount
            matched_count += 1
        else:
            # Fallback: 30% margin
            update_sql = text("""
                UPDATE sales_data
                SET profit = net_value * 0.3
                WHERE description = :product
            """)
            result = db.execute(update_sql, {"product": product})
            updated_count += result.rowcount
            fallback_count += 1
        
        # Commit every 100 products
        if i % 100 == 0:
            db.commit()
            elapsed = time.time() - start_time
            print(f"  Progress: {i:,}/{len(products):,} products ({i/len(products)*100:.1f}%) - {elapsed:.1f}s")
    
    # Final commit
    db.commit()
    
    elapsed = time.time() - start_time
    
    print(f"\n  ✅ Updated {updated_count:,} records in {elapsed:.1f}s")
    print(f"  📊 Matched with COGS: {matched_count:,} products")
    print(f"  📊 Used fallback (30%): {fallback_count:,} products")
    
    # Step 3: Verify results
    print("\n[STEP 3] Verifying results...")
    verify_query = text("""
        SELECT 
            SUM(net_value) as revenue,
            SUM(profit) as profit,
            COUNT(*) as count,
            SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as profit_count
        FROM sales_data
    """)
    result = db.execute(verify_query).fetchone()
    
    revenue = result[0] or 0
    profit = result[1] or 0
    count = result[2] or 0
    profit_count = result[3] or 0
    
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    print(f"\n  Revenue: {revenue:,.0f} VND")
    print(f"  Profit: {profit:,.0f} VND")
    print(f"  Margin: {margin:.2f}%")
    print(f"  Records with profit > 0: {profit_count:,} / {count:,}")
    
    print("\n" + "=" * 80)
    print("✅ PROFIT RECALCULATION COMPLETED")
    print("=" * 80)
    print("\nNext step: Restart backend server to refresh dashboard")
    
    db.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    db.close()
