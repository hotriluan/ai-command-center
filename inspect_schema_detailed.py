from backend.database import SessionLocal
from sqlalchemy import inspect
import json

db = SessionLocal()
inspector = inspect(db.get_bind())
tables = inspector.get_table_names()

schema_info = {}
for table in tables:
    columns = inspector.get_columns(table)
    schema_info[table] = [
        {
            'name': col['name'],
            'type': str(col['type']),
            'nullable': col['nullable']
        }
        for col in columns
    ]

print(json.dumps(schema_info, indent=2))
db.close()
