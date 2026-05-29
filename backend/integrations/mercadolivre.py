import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from config import settings
from models import Order, OrderStatus, Platform, PlatformCredential, upsert_credential

logger = logging.getLogger(__name__)

MELI_BASE = "https://api.mercadolibre.com"


async def exchange_code_for_tokens(db: Session, code: str) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MELI_BASE}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.MELI_APP_ID,
                "client_secret": settings.MELI_SECRET_KEY,
                "code": code,
                "redirect_uri": settings.MELI_REDIRECT_URI,
            },
        )
        resp.raise_for_status()
    data = resp.json()
    expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
    upsert_credential(
        db,
        Platform.MELI,
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=expires_at,
        seller_id=str(data["user_id"]),
    )


async def refresh_token_if_needed(db: Session) -> str:
    cred = db.query(PlatformCredential).filter_by(platform=Platform.MELI).first()
    if not cred or not cred.access_token:
        raise ValueError("Mercado Livre não conectado. Acesse /settings para autorizar.")

    if cred.expires_at and cred.expires_at > datetime.utcnow() + timedelta(minutes=5):
        return cred.access_token

    logger.info("Renovando token do Mercado Livre...")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MELI_BASE}/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": settings.MELI_APP_ID,
                "client_secret": settings.MELI_SECRET_KEY,
                "refresh_token": cred.refresh_token,
            },
        )
        resp.raise_for_status()
    data = resp.json()
    cred.access_token = data["access_token"]
    cred.refresh_token = data["refresh_token"]
    cred.expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
    db.commit()
    return cred.access_token


async def _paginate_orders(headers: dict, params: dict) -> list:
    orders = []
    async with httpx.AsyncClient() as client:
        while True:
            resp = await client.get(
                f"{MELI_BASE}/orders/search", headers=headers, params=params
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            orders.extend(results)
            if len(results) < 50:
                break
            params["offset"] += 50
    return orders


async def fetch_orders(db: Session, date_from: datetime, date_to: datetime) -> list:
    token = await refresh_token_if_needed(db)
    cred = db.query(PlatformCredential).filter_by(platform=Platform.MELI).first()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "seller": cred.seller_id,
        "order.date_created.from": date_from.strftime("%Y-%m-%dT%H:%M:%S.000-00:00"),
        "order.date_created.to": date_to.strftime("%Y-%m-%dT%H:%M:%S.000-00:00"),
        "limit": 50,
        "offset": 0,
    }
    orders = await _paginate_orders(headers, params)
    logger.info(f"Mercado Livre (by created): {len(orders)} pedidos encontrados")
    return orders


async def fetch_orders_by_closed(db: Session, date_from: datetime, date_to: datetime) -> list:
    token = await refresh_token_if_needed(db)
    cred = db.query(PlatformCredential).filter_by(platform=Platform.MELI).first()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "seller": cred.seller_id,
        "order.date_closed.from": date_from.strftime("%Y-%m-%dT%H:%M:%S.000-00:00"),
        "order.date_closed.to": date_to.strftime("%Y-%m-%dT%H:%M:%S.000-00:00"),
        "limit": 50,
        "offset": 0,
    }
    orders = await _paginate_orders(headers, params)
    logger.info(f"Mercado Livre (by closed): {len(orders)} pedidos encontrados")
    return orders


def map_order(raw: dict) -> dict:
    status_map = {
        "paid": OrderStatus.paid,
        "shipped": OrderStatus.shipped,
        "delivered": OrderStatus.delivered,
        "cancelled": OrderStatus.cancelled,
    }
    def to_utc(raw_str: str) -> datetime:
        return datetime.fromisoformat(raw_str.replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)

    closed_raw = raw.get("date_closed")
    return {
        "platform": Platform.MELI,
        "external_order_id": str(raw["id"]),
        "status": status_map.get(raw.get("status", ""), OrderStatus.pending),
        "total_amount": float(raw.get("total_amount", 0)),
        "currency": raw.get("currency_id", "BRL"),
        "buyer_name": raw.get("buyer", {}).get("nickname", ""),
        "created_at": to_utc(raw["date_created"]),
        "closed_at": to_utc(closed_raw) if closed_raw else None,
    }
