import httpx
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import Sale, Order, Stock, DailySummary, SyncLog

WB_STATISTICS_API = "https://statistics-api.wildberries.ru"
WB_MARKETPLACE_API = "https://marketplace-api.wildberries.ru"


class WBClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": token}
    
    async def get_sales(self, date_from: str, flag: int = 1, limit: int = 1000) -> list:
        url = f"{WB_STATISTICS_API}/api/v1/supplier/sales"
        params = {"dateFrom": date_from, "flag": flag, "limit": limit}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
    
    async def get_orders(self, date_from: str, flag: int = 1, limit: int = 1000) -> list:
        url = f"{WB_STATISTICS_API}/api/v1/supplier/orders"
        params = {"dateFrom": date_from, "flag": flag, "limit": limit}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
    
    async def get_stocks(self, date_from: str) -> list:
        url = f"{WB_STATISTICS_API}/api/v1/supplier/stocks"
        params = {"dateFrom": date_from}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()


class WBService:
    def __init__(self, db: AsyncSession, token: str):
        self.db = db
        self.client = WBClient(token)
    
    async def sync_sales(self, date_from: Optional[str] = None) -> dict:
        if not date_from:
            date_from = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        try:
            raw_data = await self.client.get_sales(date_from)
            count = 0
            for item in raw_data:
                sale_id = item.get("saleID", "")
                if not sale_id:
                    continue
                    
                exists = await self.db.execute(
                    select(Sale).where(Sale.sale_id == sale_id)
                )
                if exists.scalar_one_or_none():
                    continue
                
                sale = Sale(
                    sale_id=sale_id,
                    date=self._parse_date(item.get("date")),
                    last_change_date=self._parse_date(item.get("lastChangeDate")),
                    warehouse_name=item.get("warehouseName", ""),
                    warehouse_type=item.get("warehouseType", ""),
                    country_name=item.get("countryName", ""),
                    region_name=item.get("regionName", ""),
                    supplier_article=item.get("supplierArticle", ""),
                    nm_id=item.get("nmId", 0),
                    barcode=item.get("barcode", ""),
                    category=item.get("category", ""),
                    subject=item.get("subject", ""),
                    brand=item.get("brand", ""),
                    tech_size=item.get("techSize", ""),
                    total_price=item.get("totalPrice", 0),
                    discount_percent=item.get("discountPercent", 0),
                    spp=item.get("spp", 0),
                    payment_sale_amount=item.get("paymentSaleAmount", 0),
                    for_pay=item.get("forPay", 0),
                    finished_price=item.get("finishedPrice", 0),
                    price_with_disc=item.get("priceWithDisc", 0),
                    is_supply=item.get("isSupply", False),
                    is_realization=item.get("isRealization", False),
                )
                self.db.add(sale)
                count += 1
            
            await self.db.commit()
            
            log = SyncLog(data_type="sales", records_count=count, status="success")
            self.db.add(log)
            await self.db.commit()
            
            return {"status": "success", "new_records": count, "total": len(raw_data)}
        
        except Exception as e:
            await self.db.rollback()
            return {"status": "error", "message": str(e), "new_records": 0}
    
    async def sync_orders(self, date_from: Optional[str] = None) -> dict:
        if not date_from:
            date_from = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        try:
            raw_data = await self.client.get_orders(date_from)
            count = 0
            for item in raw_data:
                srid = item.get("srid", "")
                if not srid:
                    continue
                
                exists = await self.db.execute(
                    select(Order).where(Order.srid == srid)
                )
                if exists.scalar_one_or_none():
                    continue
                
                order = Order(
                    srid=srid,
                    date=self._parse_date(item.get("date")),
                    last_change_date=self._parse_date(item.get("lastChangeDate")),
                    warehouse_name=item.get("warehouseName", ""),
                    warehouse_type=item.get("warehouseType", ""),
                    country_name=item.get("countryName", ""),
                    region_name=item.get("regionName", ""),
                    supplier_article=item.get("supplierArticle", ""),
                    nm_id=item.get("nmId", 0),
                    barcode=item.get("barcode", ""),
                    category=item.get("category", ""),
                    subject=item.get("subject", ""),
                    brand=item.get("brand", ""),
                    tech_size=item.get("techSize", ""),
                    total_price=item.get("totalPrice", 0),
                    discount_percent=item.get("discountPercent", 0),
                    spp=item.get("spp", 0),
                    finished_price=item.get("finishedPrice", 0),
                    price_with_disc=item.get("priceWithDisc", 0),
                    is_cancel=item.get("isCancel", False),
                    cancel_date=self._parse_date(item.get("cancelDate")),
                )
                self.db.add(order)
                count += 1
            
            await self.db.commit()
            
            log = SyncLog(data_type="orders", records_count=count, status="success")
            self.db.add(log)
            await self.db.commit()
            
            return {"status": "success", "new_records": count, "total": len(raw_data)}
        
        except Exception as e:
            await self.db.rollback()
            return {"status": "error", "message": str(e), "new_records": 0}
    
    async def sync_stocks(self) -> dict:
        try:
            date_from = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
            raw_data = await self.client.get_stocks(date_from)
            count = 0
            
            # Clear old stocks and insert fresh
            await self.db.execute(Stock.__table__.delete())
            
            for item in raw_data:
                stock = Stock(
                    last_change_date=self._parse_date(item.get("lastChangeDate")),
                    warehouse_name=item.get("warehouseName", ""),
                    supplier_article=item.get("supplierArticle", ""),
                    nm_id=item.get("nmId", 0),
                    barcode=item.get("barcode", ""),
                    quantity=item.get("quantity", 0),
                    in_way_to_client=item.get("inWayToClient", 0),
                    in_way_from_client=item.get("inWayFromClient", 0),
                    quantity_full=item.get("quantityFull", 0),
                    category=item.get("category", ""),
                    subject=item.get("subject", ""),
                    brand=item.get("brand", ""),
                    tech_size=item.get("techSize", ""),
                    price=item.get("Price", 0),
                    discount=item.get("Discount", 0),
                    is_supply=item.get("isSupply", False),
                    is_realization=item.get("isRealization", False),
                )
                self.db.add(stock)
                count += 1
            
            await self.db.commit()
            
            log = SyncLog(data_type="stocks", records_count=count, status="success")
            self.db.add(log)
            await self.db.commit()
            
            return {"status": "success", "records": count}
        
        except Exception as e:
            await self.db.rollback()
            return {"status": "error", "message": str(e), "records": 0}
    
    async def calculate_daily_summary(self, date_str: str) -> dict:
        """Calculate daily summary from sales data."""
        from sqlalchemy import cast, Date
        
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Sales for this date
        sales_query = select(Sale).where(
            cast(Sale.date, Date) == target_date.date()
        )
        sales_result = await self.db.execute(sales_query)
        sales = sales_result.scalars().all()
        
        total_sales = sum(s.total_price or 0 for s in sales)
        total_for_pay = sum(s.for_pay or 0 for s in sales)
        
        # Calculate commission (total_price - for_pay roughly)
        total_commission = total_sales - total_for_pay
        
        # Orders for this date
        orders_query = select(Order).where(
            cast(Order.date, Date) == target_date.date()
        )
        orders_result = await self.db.execute(orders_query)
        orders = orders_result.scalars().all()
        
        total_orders = len(orders)
        cancelled = [o for o in orders if o.is_cancel]
        total_cancelled = len(cancelled)
        total_cancelled_amount = sum(c.total_price or 0 for c in cancelled)
        
        # Unique products
        products = set(s.nm_id for s in sales)
        product_count = len(products)
        
        # Average discount
        discounts = [s.discount_percent or 0 for s in sales]
        avg_discount = sum(discounts) / len(discounts) if discounts else 0
        
        # Upsert daily summary
        existing = await self.db.execute(
            select(DailySummary).where(
                cast(DailySummary.date, Date) == target_date.date()
            )
        )
        summary = existing.scalar_one_or_none()
        
        if summary:
            summary.total_sales = total_sales
            summary.total_orders = total_orders
            summary.total_for_pay = total_for_pay
            summary.total_commission = total_commission
            summary.total_cancelled = total_cancelled
            summary.total_cancelled_amount = total_cancelled_amount
            summary.avg_discount = avg_discount
            summary.product_count = product_count
        else:
            summary = DailySummary(
                date=target_date,
                total_sales=total_sales,
                total_orders=total_orders,
                total_for_pay=total_for_pay,
                total_commission=total_commission,
                total_cancelled=total_cancelled,
                total_cancelled_amount=total_cancelled_amount,
                avg_discount=avg_discount,
                product_count=product_count,
            )
            self.db.add(summary)
        
        await self.db.commit()
        
        return {
            "date": date_str,
            "total_sales": round(total_sales, 2),
            "total_orders": total_orders,
            "total_for_pay": round(total_for_pay, 2),
            "total_commission": round(total_commission, 2),
            "total_cancelled": total_cancelled,
        }
    
    def _parse_date(self, date_str):
        if not date_str or date_str == "0001-01-01T00:00:00":
            return None
        try:
            if "T" in date_str:
                return datetime.strptime(date_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, AttributeError):
            return None
