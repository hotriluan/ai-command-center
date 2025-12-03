from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./command_center.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=True)
    month_num = Column(Integer, nullable=True)
    month_label = Column(String, nullable=True)
    dist_channel = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    salesman_name = Column(String, nullable=True)
    product_group = Column(String, nullable=True) # PH3
    product_desc = Column(String, nullable=True) # Description
    customer_name = Column(String, nullable=True) # Name of Bill to
    revenue = Column(Float, nullable=True)

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    role = Column(String) # 'user' or 'ai'
    content = Column(Text)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
