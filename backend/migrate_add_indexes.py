"""
Migration Script: Add Performance Indexes
Phase 1A - Database Performance Optimization

This script adds missing indexes to improve query performance.
Safe to run multiple times (uses IF NOT EXISTS).
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import sys

def apply_indexes():
    """Apply performance indexes to existing database"""
    
    engine = create_engine(DATABASE_URL)
    
    indexes_to_create = [
        # SalesData indexes
        ("sales_data", "idx_sales_month_number", "month_number"),
        ("sales_data", "idx_sales_branch", "branch"),
        ("sales_data", "idx_sales_description", "description(255)"),  # Prefix index for long text
        ("sales_data", "idx_sales_year_month", "year, month_number"),
        ("sales_data", "idx_sales_year_semester", "year, month_number"),
        ("sales_data", "idx_sales_description_year", "description(255), year"),
        
        # MonthlyTarget indexes
        ("monthly_targets", "idx_monthly_year", "year"),
        ("monthly_targets", "idx_monthly_month_number", "month_number"),
        ("monthly_targets", "idx_monthly_target_lookup", "user_name(255), year, month_number"),
        
        # ARAgingReport indexes
        ("ar_aging_report", "idx_debt_salesman", "salesman_name(255)"),
        ("ar_aging_report", "idx_debt_channel", "channel"),
        ("ar_aging_report", "idx_debt_date_channel", "report_date, channel"),
    ]
    
    print("=" * 80)
    print("APPLYING PERFORMANCE INDEXES")
    print("=" * 80)
    
    with engine.connect() as conn:
        for table, index_name, columns in indexes_to_create:
            try:
                # Check if index exists
                check_query = text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE() 
                    AND table_name = :table 
                    AND index_name = :index
                """)
                
                result = conn.execute(check_query, {"table": table, "index": index_name}).scalar()
                
                if result > 0:
                    print(f"✓ Index {index_name} already exists on {table}")
                else:
                    # Create index
                    create_query = text(f"CREATE INDEX {index_name} ON {table} ({columns})")
                    conn.execute(create_query)
                    conn.commit()
                    print(f"✅ Created index {index_name} on {table}({columns})")
                    
            except Exception as e:
                print(f"❌ Error creating index {index_name}: {e}")
                continue
    
    print("\n" + "=" * 80)
    print("INDEX MIGRATION COMPLETE")
    print("=" * 80)
    
    # Verify indexes
    print("\n📊 Verifying indexes...")
    with engine.connect() as conn:
        for table in ["sales_data", "monthly_targets", "ar_aging_report"]:
            query = text(f"""
                SELECT DISTINCT index_name 
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = :table
                AND index_name != 'PRIMARY'
                ORDER BY index_name
            """)
            
            result = conn.execute(query, {"table": table}).fetchall()
            print(f"\n{table}:")
            for row in result:
                print(f"  - {row[0]}")

if __name__ == "__main__":
    try:
        print("\n⚠️  This script will add indexes to improve database performance.")
        print("It is safe to run multiple times.\n")
        
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        
        apply_indexes()
        
        print("\n✅ Migration completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Restart the backend server to use the new model definitions")
        print("   2. Run performance tests to verify improvements")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
