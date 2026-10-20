from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, BigInteger, Text, ForeignKey, UniqueConstraint
from datetime import datetime
from ..database import Base

def _now():
    return datetime.utcnow()


class Store(Base):
    """店铺：一个账号下的多个店铺，库存/箱子/日志按 store_id 隔离。"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=_now)


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


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    __table_args__ = (
        UniqueConstraint("code", "store_id", name="uq_inventory_items_code_store"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, index=True, nullable=False, default=1)   # 所属店铺
    product_name = Column(String(200), index=True)          # 产品名（用户自由输入）
    code = Column(String(200), index=True, nullable=False)  # 编码（扫描目标，店铺内唯一）
    quantity = Column(Integer, default=0)                   # 正品库存
    defective_quantity = Column(Integer, default=0)         # 次品库存
    remark = Column(String(500))                            # 备注
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class InventoryLog(Base):
    """库存操作日志（发货 / 退货），按天统计与查询。"""
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, index=True, nullable=False, default=1)   # 所属店铺
    code = Column(String(200), index=True)                  # 编码（扫描目标）
    product_name = Column(String(200))                      # 产品名快照（便于统计，即使原项被删）
    action = Column(String(20), index=True)                 # ship=发货 / return=退货
    delta = Column(Integer)                                 # 变更量 -1 / +1
    quantity_after = Column(Integer)                        # 操作后正品库存
    defect_after = Column(Integer)                          # 操作后次品库存
    from_defect = Column(Boolean, default=False)            # 发货是否取自次品库存
    box_id = Column(Integer)                                # 调拨来源箱子 id（仅调拨）
    box_code = Column(String(200))                          # 调拨来源箱唛快照（仅调拨）
    log_date = Column(String(10), index=True)               # YYYY-MM-DD（用于按天统计）
    created_at = Column(DateTime, default=_now, index=True)


class Box(Base):
    """箱子库存：一个箱子（箱唛编码在店铺内唯一）一条记录，含箱级备注；下面挂多个产品型号。"""
    __tablename__ = "boxes"
    __table_args__ = (
        UniqueConstraint("box_code", "store_id", name="uq_boxes_box_code_store"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, index=True, nullable=False, default=1)   # 所属店铺
    box_code = Column(String(200), index=True, nullable=False)  # 箱唛编码（店铺内唯一）
    remark = Column(String(500))                                            # 箱级备注
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class BoxItem(Base):
    """箱子里的产品型号 + 初始库存。"""
    __tablename__ = "box_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    box_id = Column(Integer, ForeignKey("boxes.id"), index=True, nullable=False)
    product_model = Column(String(200))                     # 产品型号
    quantity = Column(Integer, default=0)                   # 初始库存
    created_at = Column(DateTime, default=_now)
