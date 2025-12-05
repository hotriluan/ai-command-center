"""
Create AR Aging Report Table
Run this script to create the ar_aging_report table in the database
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import Base, engine
from models import ARAgingReport

def create_debt_table():
    print("Creating ar_aging_report table...")
    Base.metadata.create_all(bind=engine)
    print("✓ Table created successfully")

if __name__ == "__main__":
    create_debt_table()
