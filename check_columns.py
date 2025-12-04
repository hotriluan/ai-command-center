import pandas as pd

try:
    df = pd.read_excel('demodata/zrsd002_11.xlsx')
    cols = list(df.columns)
    
    print("-" * 50)
    print("FILE ANALYSIS: zrsd002_11.xlsx")
    print("-" * 50)
    
    required = ['Net Value', 'Billing Qty', 'Description']
    for req in required:
        if req in cols:
            print(f"✅ Found column: '{req}'")
        else:
            print(f"❌ MISSING column: '{req}'")
            
    print(f"\nTotal Columns: {len(cols)}")
    print(f"Column List: {cols}")
    
except Exception as e:
    print(f"Error reading file: {e}")
