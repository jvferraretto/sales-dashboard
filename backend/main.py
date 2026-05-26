import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Sales Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    start_scheduler()


from api.orders import router as orders_router
from api.dashboard import router as dashboard_router
from api.sync import router as sync_router
from api.credentials import router as credentials_router
from api.auth.mercadolivre import router as meli_auth_router
from api.auth.shopee import router as shopee_auth_router

app.include_router(orders_router, prefix="/orders", tags=["orders"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(sync_router, prefix="/sync", tags=["sync"])
app.include_router(credentials_router, prefix="/credentials", tags=["credentials"])
app.include_router(meli_auth_router, prefix="/auth/mercadolivre", tags=["auth"])
app.include_router(shopee_auth_router, prefix="/auth/shopee", tags=["auth"])


@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}
