import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database import SessionLocal
from models import Order, Platform, SyncLog

logger = logging.getLogger(__name__)
_scheduler = BackgroundScheduler()


def sync_platform(platform: str) -> None:
    import integrations.mercadolivre as ml
    import integrations.shopee as sp

    db = SessionLocal()
    log = SyncLog(platform=platform, status="running", orders_fetched=0)
    db.add(log)
    db.commit()

    try:
        now = datetime.utcnow()
        since = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

        if platform == Platform.MELI:
            # Busca por date_created E por date_closed para capturar pedidos pagos hoje
            raw_by_created = asyncio.run(ml.fetch_orders(db, since, now))
            raw_by_closed = asyncio.run(ml.fetch_orders_by_closed(db, since, now))
            seen_ids = set()
            raw_orders = []
            for o in raw_by_created + raw_by_closed:
                if o["id"] not in seen_ids:
                    seen_ids.add(o["id"])
                    raw_orders.append(o)
            mapped = [ml.map_order(o) for o in raw_orders]
        else:
            raw_orders = asyncio.run(
                sp.fetch_orders(db, int(since.timestamp()), int(now.timestamp()))
            )
            mapped = [sp.map_order(o) for o in raw_orders]

        saved = 0
        for data in mapped:
            existing = (
                db.query(Order)
                .filter_by(external_order_id=data["external_order_id"])
                .first()
            )
            if existing:
                existing.status = data["status"]
                if data.get("closed_at"):
                    existing.closed_at = data["closed_at"]
            else:
                db.add(Order(**data))
                saved += 1
        db.commit()

        log.orders_fetched = saved
        log.status = "success"
        db.commit()
        logger.info(f"Sync {platform}: {saved} novos pedidos salvos")

    except Exception as exc:
        log.status = "error"
        log.error_message = str(exc)
        db.commit()
        logger.error(f"Sync {platform} falhou: {exc}")
    finally:
        db.close()


def sync_all() -> None:
    sync_platform(Platform.MELI)
    sync_platform(Platform.SHOPEE)


def start_scheduler() -> None:
    _scheduler.add_job(
        sync_all,
        CronTrigger(hour=2, minute=0),
        id="daily_sync",
        replace_existing=True,
    )
    # Sync a cada 2 minutos entre 06:00 e 23:00 horário Brasília (09:00–02:00 UTC)
    _scheduler.add_job(
        sync_all,
        CronTrigger(minute="*/2", hour="9-23,0,1,2"),
        id="frequent_sync",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("APScheduler iniciado — sync a cada 15 min (06h–23h) e diário às 02:00 UTC")
