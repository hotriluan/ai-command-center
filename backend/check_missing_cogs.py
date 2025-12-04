"""
Check missing COGS report and create sample COGS file
"""
import pandas as pd
import os

# Check if report exists
report_path = os.path.join(os.path.dirname(__file__), 'missing_cogs_report.xlsx')

if os.path.exists(report_path):
    print("=" * 80)
    print("MISSING COGS REPORT")
    print("=" * 80)
    
    df = pd.read_excel(report_path)
    print(f"\nTotal missing products: {len(df)}")
    print("\nFirst 10 products:")
    print(df.head(10).to_string())
    
    # Create sample COGS file
    print("\n" + "=" * 80)
    print("CREATING SAMPLE COGS FILE")
    print("=" * 80)
    
    # Add sample COGS prices (you can adjust these)
    df['COGS'] = 1000  # Default COGS
    df = df.rename(columns={'material_code': 'Material', 'description': 'Description'})
    
    cogs_file = os.path.join(os.path.dirname(__file__), '..', 'demodata', 'cogs_sample.xlsx')
    df[['Material', 'Description', 'COGS']].to_excel(cogs_file, index=False)
    
    print(f"\n✅ Created: {cogs_file}")
    print(f"   Rows: {len(df)}")
    print("\nNext steps:")
    print("1. Review and adjust COGS prices in cogs_sample.xlsx")
    print("2. Import COGS: curl -X POST http://localhost:8000/api/import/cogs -F 'file=@demodata/cogs_sample.xlsx'")
    print("3. Retry sales import")
    
else:
    print("❌ Report not found")
