import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class Platform(str, enum.Enum):
    MELI = "MELI"
    SHOPEE = "SHOPEE"


class OrderStatus(str, enum.Enum):
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    pending = "pending"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(Platform), nullable=False, index=True)
    external_order_id = Column(String(128), unique=True, nullable=False, index=True)
    status = Column(Enum(OrderStatus), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(8), default="BRL")
    buyer_name = Column(String(256))
    created_at = Column(DateTime, nullable=False, index=True)
    synced_at = Column(DateTime, server_default=func.now())


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(Platform), nullable=False)
    synced_at = Column(DateTime, server_default=func.now())
    orders_fetched = Column(Integer, default=0)
    status = Column(String(16))
    error_message = Column(Text, nullable=True)


class PlatformCredential(Base):
    __tablename__ = "platform_credentials"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(Platform), unique=True, nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    seller_id = Column(String(64), nullable=True)
    shop_id = Column(String(64), nullable=True)


def upsert_credential(db, platform, **kwargs):
    cred = db.query(PlatformCredential).filter_by(platform=platform).first()
    if cred:
        for k, v in kwargs.items():
            setattr(cred, k, v)
    else:
        cred = PlatformCredential(platform=platform, **kwargs)
        db.add(cred)
    db.commit()
    db.refresh(cred)
    return cred
