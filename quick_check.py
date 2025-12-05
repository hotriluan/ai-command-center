"""Minimal channel check - key info only"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT DISTINCT dist FROM sales_data LIMIT 10"))
print("DIST VALUES:")
for row in result:
    val = row[0]
    print(f"{repr(val)} ({type(val).__name__})")
db.close()
