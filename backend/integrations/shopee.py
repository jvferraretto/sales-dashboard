import hashlib
import hmac
import logging
import time
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from config import settings
from models import OrderStatus, Platform, PlatformCredential, upsert_credential

logger = logging.getLogger(__name__)

SHOPEE_BASE = "https://partner.shopeemobile.com"


def sign_public(path: str, timestamp: int) -> str:
    base = f"{settings.SHOPEE_PARTNER_ID}{path}{timestamp}"
    return hmac.new(
        settings.SHOPEE_PARTNER_KEY.encode(),
        base.encode(),
        hashlib.sha256,
    ).hexdigest()


def sign_shop(path: str, timestamp: int, access_token: str, shop_id: int) -> str:
    base = f"{settings.SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    return hmac.new(
        settings.SHOPEE_PARTNER_KEY.encode(),
        base.encode(),
        hashlib.sha256,
    ).hexdigest()


async def exchange_code_for_tokens(db: Session, code: str, shop_id: int) -> None:
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    sign = sign_public(path, timestamp)
    payload = {
        "code": code,
        "shop_id": shop_id,
        "partner_id": int(settings.SHOPEE_PARTNER_ID),
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SHOPEE_BASE}{path}",
            params={
                "partner_id": settings.SHOPEE_PARTNER_ID,
                "timestamp": timestamp,
                "sign": sign,
            },
            json=payload,
        )
        resp.raise_for_status()
    data = resp.json()
    expires_at = datetime.utcnow() + timedelta(seconds=data.get("expire_in", 14400))
    upsert_credential(
        db,
        Platform.SHOPEE,
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=expires_at,
        shop_id=str(shop_id),
    )


async def refresh_token_if_needed(db: Session) -> str:
    cred = db.query(PlatformCredential).filter_by(platform=Platform.SHOPEE).first()
    if not cred or not cred.access_token:
        raise ValueError("Shopee não conectada. Acesse /settings para autorizar.")

    if cred.expires_at and cred.expires_at > datetime.utcnow() + timedelta(minutes=5):
        return cred.access_token

    logger.info("Renovando token da Shopee...")
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = sign_public(path, timestamp)
    payload = {
        "refresh_token": cred.refresh_token,
        "partner_id": int(settings.SHOPEE_PARTNER_ID),
        "shop_id": int(cred.shop_id),
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SHOPEE_BASE}{path}",
            params={
                "partner_id": settings.SHOPEE_PARTNER_ID,
                "timestamp": timestamp,
                "sign": sign,
            },
            json=payload,
        )
        resp.raise_for_status()
    data = resp.json()
    cred.access_token = data["access_token"]
    cred.refresh_token = data["refresh_token"]
    cred.expires_at = datetime.utcnow() + timedelta(seconds=data.get("expire_in", 14400))
    db.commit()
    return cred.access_token


async def fetch_orders(db: Session, time_from: int, time_to: int) -> list:
    token = await refresh_token_if_needed(db)
    cred = db.query(PlatformCredential).filter_by(platform=Platform.SHOPEE).first()
    shop_id = int(cred.shop_id)
    path = "/api/v2/order/get_order_list"

    order_sns, cursor = [], ""
    async with httpx.AsyncClient() as client:
        while True:
            timestamp = int(time.time())
            sign = sign_shop(path, timestamp, token, shop_id)
            payload = {
                "time_range_field": "create_time",
                "time_from": time_from,
                "time_to": time_to,
                "page_size": 50,
                "cursor": cursor,
            }
            resp = await client.post(
                f"{SHOPEE_BASE}{path}",
                params={
                    "partner_id": settings.SHOPEE_PARTNER_ID,
                    "timestamp": timestamp,
                    "sign": sign,
                    "access_token": token,
                    "shop_id": shop_id,
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json().get("response", {})
            order_sns.extend(data.get("order_list", []))
            if not data.get("more", False):
                break
            cursor = data["next_cursor"]

    if not order_sns:
        return []

    # Busca detalhes em batches de 50 para obter total_amount
    all_orders = []
    detail_path = "/api/v2/order/get_order_detail"
    for i in range(0, len(order_sns), 50):
        batch = order_sns[i : i + 50]
        sns = [o["order_sn"] for o in batch]
        timestamp = int(time.time())
        sign = sign_shop(detail_path, timestamp, token, shop_id)
        payload = {"order_sn_list": sns}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{SHOPEE_BASE}{detail_path}",
                params={
                    "partner_id": settings.SHOPEE_PARTNER_ID,
                    "timestamp": timestamp,
                    "sign": sign,
                    "access_token": token,
                    "shop_id": shop_id,
                },
                json=payload,
            )
            resp.raise_for_status()
        detail_data = resp.json().get("response", {}).get("order_list", [])
        all_orders.extend(detail_data)

    logger.info(f"Shopee: {len(all_orders)} pedidos encontrados")
    return all_orders


SHOPEE_STATUS_MAP = {
    "READY_TO_SHIP": OrderStatus.paid,
    "PROCESSED": OrderStatus.paid,
    "SHIPPED": OrderStatus.shipped,
    "COMPLETED": OrderStatus.delivered,
    "CANCELLED": OrderStatus.cancelled,
    "UNPAID": OrderStatus.pending,
    "TO_CONFIRM_RECEIVE": OrderStatus.shipped,
    "IN_CANCEL": OrderStatus.pending,
}


def map_order(raw: dict) -> dict:
    return {
        "platform": Platform.SHOPEE,
        "external_order_id": raw["order_sn"],
        "status": SHOPEE_STATUS_MAP.get(raw.get("order_status", ""), OrderStatus.pending),
        "total_amount": float(raw.get("total_amount", 0)) / 100,
        "currency": "BRL",
        "buyer_name": raw.get("buyer_username", ""),
        "created_at": datetime.utcfromtimestamp(raw["create_time"]),
    }
