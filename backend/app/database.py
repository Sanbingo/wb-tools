from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from passlib.hash import bcrypt
from .config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        from .models import Sale, Order, Stock, DailySummary, SyncLog, User, InventoryItem, InventoryLog, Box, BoxItem, Store, InboundWaybill, InboundItem  # noqa
        await conn.run_sync(Base.metadata.create_all)
        # 轻量迁移（无迁移框架）：为已存在的表按需补充新增列
        res = await conn.exec_driver_sql("PRAGMA table_info(inbound_waybills)")
        _cols = [row[1] for row in res.fetchall()]
        if _cols and "remark" not in _cols:
            await conn.exec_driver_sql("ALTER TABLE inbound_waybills ADD COLUMN remark VARCHAR(500)")
        # 送仓明细：补充「来源箱子库存明细行 id」（精确到某一包）
        res2 = await conn.exec_driver_sql("PRAGMA table_info(delivery_plan_items)")
        _cols2 = [row[1] for row in res2.fetchall()]
        if _cols2 and "box_item_id" not in _cols2:
            await conn.exec_driver_sql("ALTER TABLE delivery_plan_items ADD COLUMN box_item_id INTEGER")
        if _cols2 and "box_code" not in _cols2:
            await conn.exec_driver_sql("ALTER TABLE delivery_plan_items ADD COLUMN box_code VARCHAR(200)")
        # 送仓箱子：补充「外箱编码」（用户手工填写）
        res3 = await conn.exec_driver_sql("PRAGMA table_info(delivery_plan_boxes)")
        _cols3 = [row[1] for row in res3.fetchall()]
        if _cols3 and "outer_code" not in _cols3:
            await conn.exec_driver_sql("ALTER TABLE delivery_plan_boxes ADD COLUMN outer_code VARCHAR(200)")

    # Seed default user
    async with async_session() as session:
        from .models import User, Store
        existing = await session.execute(select(User).where(User.username == "WB"))
        if not existing.scalar_one_or_none():
            session.add(User(username="WB", password_hash=bcrypt.hash("000111")))
            await session.commit()
        # Seed 店铺1（现有/历史数据的归属店铺）
        has_store = await session.execute(select(Store).limit(1))
        if not has_store.scalar_one_or_none():
            session.add(Store(name="店铺1"))
            await session.commit()
