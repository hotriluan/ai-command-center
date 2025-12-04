from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from database import Base

class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=True)
    month = Column(String, nullable=True) # e.g. 'Jan'
    month_number = Column(Integer, nullable=True)
    dist = Column(String, nullable=True) # Channel
    branch = Column(String, nullable=True)
    salesman_name = Column(String, nullable=True)
    product_group = Column(String, nullable=True) # PH3
    description = Column(String, nullable=True) # Product Name
    customer_name = Column(String, nullable=True)
    billing_qty = Column(Float, nullable=True)
    net_value = Column(Float, nullable=True) # Revenue
    profit = Column(Float, nullable=True)
    marketing_spend = Column(Float, nullable=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    role = Column(String) # 'user' or 'ai'
    content = Column(Text)

class ProductCost(Base):
    __tablename__ = "product_cost"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, unique=True, index=True, nullable=False)
    cogs = Column(Float, nullable=False)

class SalesTarget(Base):
    __tablename__ = "sales_target"

    id = Column(Integer, primary_key=True, index=True)
    salesman_name = Column(String, index=True, nullable=False)
    semester = Column(Integer, nullable=False) # 1 or 2
    target_amount = Column(Float, nullable=False)
    year = Column(Integer, default=2025, nullable=False)
