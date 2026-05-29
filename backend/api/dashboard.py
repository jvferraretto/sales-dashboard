from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Order, OrderStatus, Platform
from schemas import ChartPoint, KpiPeriod, KpisOut, RevenuePoint

router = APIRouter()

BR_TZ_OFFSET = timedelta(hours=-3)
EXCLUDED_STATUSES = [OrderStatus.cancelled]


def _now_br() -> datetime:
    """Retorna datetime atual no horário de Brasília (UTC-3), sem tzinfo."""
    return datetime.now(timezone.utc).replace(tzinfo=None) + BR_TZ_OFFSET


def _active_orders(db: Session):
    return db.query(Order).filter(Order.status.notin_(EXCLUDED_STATUSES))


@router.get("/kpis", response_model=KpisOut)
def get_kpis(db: Session = Depends(get_db)):
    now = _now_br()
    periods = {
        "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "week": now - timedelta(days=7),
        "month": now - timedelta(days=30),
    }
    result = {}
    for label, since in periods.items():
        since_utc = since - BR_TZ_OFFSET
        # "hoje" usa closed_at (igual ao painel ML); semana/mês usam created_at
        date_col = Order.closed_at if label == "today" else Order.created_at
        row = db.query(
            func.count(Order.id).label("count"),
            func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
        ).filter(
            date_col >= since_utc,
            Order.status.notin_(EXCLUDED_STATUSES),
        ).first()
        result[label] = KpiPeriod(orders=row.count, revenue=float(row.revenue))
    return KpisOut(**result)


@router.get("/chart-data", response_model=List[ChartPoint])
def get_chart_data(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    since_utc = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    rows = (
        db.query(
            func.date(Order.created_at).label("day"),
            Order.platform,
            func.count(Order.id).label("count"),
        )
        .filter(
            Order.created_at >= since_utc,
            Order.status.notin_(EXCLUDED_STATUSES),
        )
        .group_by(func.date(Order.created_at), Order.platform)
        .order_by("day")
        .all()
    )
    return [ChartPoint(day=str(r.day), platform=r.platform, count=r.count) for r in rows]


@router.get("/revenue-trend", response_model=List[RevenuePoint])
def get_revenue_trend(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    since_utc = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    rows = (
        db.query(
            func.date(Order.created_at).label("day"),
            Order.platform,
            func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
        )
        .filter(
            Order.created_at >= since_utc,
            Order.status.notin_(EXCLUDED_STATUSES),
        )
        .group_by(func.date(Order.created_at), Order.platform)
        .order_by("day")
        .all()
    )
    return [
        RevenuePoint(day=str(r.day), platform=r.platform, revenue=float(r.revenue))
        for r in rows
    ]
