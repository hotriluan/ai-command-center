from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check for the 3 missing products
missing_products = [
    'PUC-54205 AC WHITE 15 VN-20KP',
    'PUH-56142 SP VN-20KP',
    'PUP-52142 ACR WHITE SP VN-20KP'
]

print("Checking for missing products in database:\n")

for product in missing_products:
    result = db.execute(
        text("SELECT description, cogs FROM product_cost WHERE description = :desc"),
        {"desc": product}
    ).fetchone()
    
    if result:
        print(f"✅ FOUND: {product}")
        print(f"   COGS: {result[1]}")
    else:
        print(f"❌ NOT FOUND: {product}")
        
        # Try fuzzy search
        fuzzy_result = db.execute(
            text("SELECT description, cogs FROM product_cost WHERE description LIKE :pattern LIMIT 3"),
            {"pattern": f"%{product[:20]}%"}
        ).fetchall()
        
        if fuzzy_result:
            print(f"   Similar products found:")
            for row in fuzzy_result:
                print(f"     - {row[0]}")

print(f"\nTotal COGS records in database:")
count = db.execute(text("SELECT COUNT(*) FROM product_cost")).scalar()
print(f"  {count:,} records")

db.close()
