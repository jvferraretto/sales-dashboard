from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models import OrderStatus, Platform


class OrderOut(BaseModel):
    id: int
    platform: Platform
    external_order_id: str
    status: OrderStatus
    total_amount: float
    currency: str
    buyer_name: Optional[str]
    created_at: datetime
    synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrdersPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[OrderOut]


class KpiPeriod(BaseModel):
    orders: int
    revenue: float


class KpisOut(BaseModel):
    today: KpiPeriod
    week: KpiPeriod
    month: KpiPeriod


class ChartPoint(BaseModel):
    day: str
    platform: Platform
    count: int


class RevenuePoint(BaseModel):
    day: str
    platform: Platform
    revenue: float


class SyncStatusEntry(BaseModel):
    last_synced_at: Optional[str]
    status: str
    orders_fetched: int
    error_message: Optional[str]


class CredentialStatus(BaseModel):
    connected: bool
    seller_id: Optional[str] = None
    shop_id: Optional[str] = None
    expires_at: Optional[datetime] = None
