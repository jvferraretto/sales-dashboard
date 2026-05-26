from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Order, OrderStatus, Platform
from schemas import OrderOut, OrdersPage

router = APIRouter()


@router.get("", response_model=OrdersPage)
def list_orders(
    platform: Optional[Platform] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    if platform:
        query = query.filter(Order.platform == platform)
    if status:
        query = query.filter(Order.status == status)
    if date_from:
        query = query.filter(Order.created_at >= date_from)
    if date_to:
        query = query.filter(Order.created_at <= date_to)

    total = query.count()
    items = (
        query.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return OrdersPage(total=total, page=page, page_size=page_size, items=items)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
