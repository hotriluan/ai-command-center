from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Date, Index
from datetime import datetime
from database import Base

class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Transaction identifiers
    billing_document = Column(String(100), nullable=True, index=True)
    billing_item = Column(String(100), nullable=True)
    material_code = Column(String(100), nullable=True, index=True)
    so_no = Column(String(100), nullable=True, index=True)  # Sales Order Number
    
    # Dates
    billing_date = Column(String(20), nullable=True)
    so_date = Column(String(20), nullable=True)
    
    # Time dimensions
    year = Column(Integer, nullable=True, index=True)
    month = Column(String(20), nullable=True)  # e.g. 'Jan'
    month_number = Column(Integer, nullable=True, index=True)  # PERFORMANCE: Added index for frequent filtering
    
    # Organizational dimensions
    dist = Column(String(100), nullable=True, index=True)  # Channel
    branch = Column(String(100), nullable=True, index=True)  # PERFORMANCE: Added index for branch aggregations
    salesman_name = Column(String(255), nullable=True, index=True)
    
    # Product dimensions
    product_group = Column(String(100), nullable=True)  # PH3
    description = Column(String(500), nullable=True, index=True)  # PERFORMANCE: Added index for product lookups and COGS joins
    
    # Customer
    customer_name = Column(String(255), nullable=True, index=True)
    
    # Metrics
    billing_qty = Column(Float, nullable=True)
    net_value = Column(Float, nullable=True)  # Revenue
    profit = Column(Float, nullable=True, default=0)
    marketing_spend = Column(Float, nullable=True, default=0)
    
    # PERFORMANCE: Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_sales_year_month', 'year', 'month_number'),  # For time-based queries
        Index('idx_sales_year_semester', 'year', 'month_number'),  # For semester filtering (month_number <= 6)
        Index('idx_sales_description_year', 'description', 'year'),  # For product analysis over time
    )



class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    role = Column(String(20)) # 'user' or 'ai'
    content = Column(Text)

class ProductCost(Base):
    __tablename__ = "product_cost"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(500), index=True, nullable=False)
    cogs = Column(Float, nullable=False)

class SalesTarget(Base):
    __tablename__ = "sales_target"

    id = Column(Integer, primary_key=True, index=True)
    salesman_name = Column(String(255), index=True, nullable=False)
    semester = Column(Integer, nullable=False) # 1 or 2
    target_amount = Column(Float, nullable=False)
    year = Column(Integer, default=2025, nullable=False)

class MonthlyTarget(Base):
    __tablename__ = "monthly_targets"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(255), index=True, nullable=False)
    year = Column(Integer, nullable=False, index=True)  # PERFORMANCE: Added index for year filtering
    month_number = Column(Integer, nullable=False, index=True)  # PERFORMANCE: Added index for month lookups
    target_amount = Column(Float, nullable=False)
    semester = Column(Integer, nullable=False) # 1 or 2
    
    # PERFORMANCE: Composite index for target lookups
    __table_args__ = (
        Index('idx_monthly_target_lookup', 'user_name', 'year', 'month_number'),  # For fast target retrieval
    )

class ARAgingReport(Base):
    __tablename__ = "ar_aging_report"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(String(20), nullable=False, index=True)  # YYYY-MM-DD format
    salesman_name = Column(String(255), nullable=True, index=True)  # PERFORMANCE: Added index for salesman filtering
    customer_name = Column(String(255), nullable=False)
    customer_code = Column(String(100), nullable=False, index=True)
    channel = Column(String(50), nullable=False, index=True)  # PERFORMANCE: Added index for channel aggregations
    total_debt = Column(Float, default=0)
    total_realization = Column(Float, default=0)
    debt_1_30 = Column(Float, default=0)
    debt_31_60 = Column(Float, default=0)
    debt_61_90 = Column(Float, default=0)
    debt_91_120 = Column(Float, default=0)
    debt_121_180 = Column(Float, default=0)
    debt_over_180 = Column(Float, default=0)
    
    # PERFORMANCE: Composite index for debt analysis queries
    __table_args__ = (
        Index('idx_debt_date_channel', 'report_date', 'channel'),  # For channel breakdown by date
    )


