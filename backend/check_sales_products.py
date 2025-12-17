import pandas as pd

# Read sales file
sales_df = pd.read_excel(r'c:\dev\ai-command-center\demodata\zrsd0021612.xlsx', engine='openpyxl')

# Get the 3 problematic products
problem_products = [
    'PUC-54205 AC WHITE 15 VN-20KP',
    'PUH-56142 SP VN-20KP',
    'PUP-52142 ACR WHITE SP VN-20KP'
]

print("Checking product names in sales file:\n")

for product in problem_products:
    # Find in sales file
    matches = sales_df[sales_df['Description'].str.contains(product[:15], na=False)]
    
    if len(matches) > 0:
        actual_name = matches.iloc[0]['Description']
        print(f"Product: {product}")
        print(f"  In sales file: '{actual_name}'")
        print(f"  Length: {len(actual_name)} vs {len(product)}")
        print(f"  Match: {actual_name == product}")
        print(f"  Repr: {repr(actual_name)}")
        print()
