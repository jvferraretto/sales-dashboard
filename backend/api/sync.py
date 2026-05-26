from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Platform, SyncLog
from schemas import SyncStatusEntry

router = APIRouter()


class SyncTriggerBody(BaseModel):
    platform: Optional[Platform] = None


@router.post("/trigger")
def trigger_sync(body: SyncTriggerBody = SyncTriggerBody(), background_tasks: BackgroundTasks = BackgroundTasks()):
    from scheduler import sync_all, sync_platform

    if body.platform:
        background_tasks.add_task(sync_platform, body.platform)
    else:
        background_tasks.add_task(sync_all)
    return {"message": "Sync started", "platform": body.platform or "all"}


@router.get("/status", response_model=Dict[str, SyncStatusEntry])
def sync_status(db: Session = Depends(get_db)):
    result = {}
    for p in [Platform.MELI, Platform.SHOPEE]:
        last = (
            db.query(SyncLog)
            .filter(SyncLog.platform == p)
            .order_by(SyncLog.synced_at.desc())
            .first()
        )
        result[p.value] = SyncStatusEntry(
            last_synced_at=last.synced_at.isoformat() if last else None,
            status=last.status if last else "never",
            orders_fetched=last.orders_fetched if last else 0,
            error_message=last.error_message if last else None,
        )
    return result
