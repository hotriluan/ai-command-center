from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./command_center.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Check SalesData count
    result = db.execute(text("SELECT COUNT(*) FROM sales_data")).scalar()
    print(f"Total rows in SalesData: {result}")

    # Check sample data
    if result > 0:
        sample = db.execute(text("SELECT * FROM sales_data LIMIT 1")).fetchone()
        print(f"Sample row: {sample}")
    
    # Check ChatHistory count (optional, just to see if chat is working too if they used it)
    chat_count = db.execute(text("SELECT COUNT(*) FROM chat_history")).scalar()
    print(f"Total chat messages: {chat_count}")

except Exception as e:
    print(f"Error checking DB: {e}")
finally:
    db.close()
