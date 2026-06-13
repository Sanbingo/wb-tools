from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, BigInteger, Text
from datetime import datetime
from ..database import Base

def _now():
    return datetime.utcnow()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=_now)


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(String(50), unique=True, index=True)
    date = Column(DateTime, index=True)
    last_change_date = Column(DateTime)
    warehouse_name = Column(String(100))
    warehouse_type = Column(String(50))
    country_name = Column(String(50))
    region_name = Column(String(100))
    supplier_article = Column(String(200))
    nm_id = Column(BigInteger, index=True)
    barcode = Column(String(100))
    category = Column(String(100))
    subject = Column(String(100))
    brand = Column(String(100))
    tech_size = Column(String(50))
    total_price = Column(Float)
    discount_percent = Column(Integer)
    spp = Column(Integer)
    payment_sale_amount = Column(Float)
    for_pay = Column(Float)
    finished_price = Column(Float)
    price_with_disc = Column(Float)
    is_supply = Column(Boolean)
    is_realization = Column(Boolean)
    created_at = Column(DateTime, default=_now)


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    srid = Column(String(100), unique=True, index=True)
    date = Column(DateTime, index=True)
    last_change_date = Column(DateTime)
    warehouse_name = Column(String(100))
    warehouse_type = Column(String(50))
    country_name = Column(String(50))
    region_name = Column(String(100))
    supplier_article = Column(String(200))
    nm_id = Column(BigInteger, index=True)
    barcode = Column(String(100))
    category = Column(String(100))
    subject = Column(String(100))
    brand = Column(String(100))
    tech_size = Column(String(50))
    total_price = Column(Float)
    discount_percent = Column(Integer)
    spp = Column(Integer)
    finished_price = Column(Float)
    price_with_disc = Column(Float)
    is_cancel = Column(Boolean)
    cancel_date = Column(DateTime)
    created_at = Column(DateTime, default=_now)


class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_change_date = Column(DateTime)
    warehouse_name = Column(String(100))
    supplier_article = Column(String(200))
    nm_id = Column(BigInteger, index=True)
    barcode = Column(String(100))
    quantity = Column(Integer)
    in_way_to_client = Column(Integer)
    in_way_from_client = Column(Integer)
    quantity_full = Column(Integer)
    category = Column(String(100))
    subject = Column(String(100))
    brand = Column(String(100))
    tech_size = Column(String(50))
    price = Column(Float)
    discount = Column(Integer)
    is_supply = Column(Boolean)
    is_realization = Column(Boolean)
    created_at = Column(DateTime, default=_now)


class SyncLog(Base):
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_type = Column(String(50), index=True)
    records_count = Column(Integer)
    status = Column(String(20))  # success, error
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=_now)


class DailySummary(Base):
    __tablename__ = "daily_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, index=True, unique=True)
    total_sales = Column(Float, default=0)
    total_orders = Column(Integer, default=0)
    total_for_pay = Column(Float, default=0)
    total_commission = Column(Float, default=0)
    total_cancelled = Column(Integer, default=0)
    total_cancelled_amount = Column(Float, default=0)
    avg_discount = Column(Float, default=0)
    product_count = Column(Integer, default=0)


class UploadedReport(Base):
    __tablename__ = "uploaded_reports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(200))
    file_type = Column(String(20), default="platform")  # platform or purchase
    period_start = Column(DateTime, index=True)
    period_end = Column(DateTime, index=True)
    total_sales = Column(Float, default=0)
    total_for_pay = Column(Float, default=0)
    total_commission = Column(Float, default=0)
    total_logistics = Column(Float, default=0)
    total_storage = Column(Float, default=0)
    records_count = Column(Integer, default=0)
    source = Column(String(20), default="upload")  # upload or api
    uploaded_at = Column(DateTime, default=_now)
    file_path = Column(String(500), nullable=True)
    purchase_file_path = Column(String(500), nullable=True)
