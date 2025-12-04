from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./command_center_v2.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    # Import models here to ensure they are registered with Base.metadata
    from models import SalesData, ChatHistory, ProductCost, SalesTarget
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
