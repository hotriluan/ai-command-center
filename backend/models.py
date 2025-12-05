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

class MonthlyTarget(Base):
    __tablename__ = "monthly_targets"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    month_number = Column(Integer, nullable=False)
    target_amount = Column(Float, nullable=False)
    semester = Column(Integer, nullable=False) # 1 or 2

class ARAgingReport(Base):
    __tablename__ = "ar_aging_report"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(String, nullable=False, index=True)  # YYYY-MM-DD format
    salesman_name = Column(String, nullable=True)
    customer_name = Column(String, nullable=False)
    customer_code = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=False)  # 'Industry', 'Retail', 'Project', 'Others'
    total_debt = Column(Float, default=0)
    total_realization = Column(Float, default=0)
    debt_1_30 = Column(Float, default=0)
    debt_31_60 = Column(Float, default=0)
    debt_61_90 = Column(Float, default=0)
    debt_91_120 = Column(Float, default=0)
    debt_121_180 = Column(Float, default=0)
    debt_over_180 = Column(Float, default=0)
