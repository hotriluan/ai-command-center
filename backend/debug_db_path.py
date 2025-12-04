"""
Debug script to check database path and tables
"""
import sqlite3
import os

# Try both possible database locations
db_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'command_center.db'),
    os.path.join(os.path.dirname(__file__), 'command_center.db'),
    'command_center.db',
    '../command_center.db'
]

for db_path in db_paths:
    abs_path = os.path.abspath(db_path)
    print(f"\nChecking: {abs_path}")
    if os.path.exists(abs_path):
        print(f"  ✅ EXISTS")
        try:
            conn = sqlite3.connect(abs_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"  Tables: {tables}")
            conn.close()
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print(f"  ❌ NOT FOUND")
