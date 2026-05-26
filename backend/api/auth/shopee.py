import time
from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from integrations.shopee import exchange_code_for_tokens, sign_public

router = APIRouter()

SHOPEE_BASE = "https://partner.shopeemobile.com"


@router.get("/login")
def shopee_login():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = sign_public(path, timestamp)
    params = {
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign,
        "redirect": settings.SHOPEE_REDIRECT_URI,
    }
    return RedirectResponse(f"{SHOPEE_BASE}{path}?{urlencode(params)}")


@router.get("/callback")
async def shopee_callback(code: str, shop_id: int, db: Session = Depends(get_db)):
    await exchange_code_for_tokens(db, code, shop_id)
    return RedirectResponse("http://localhost:3000/settings?shopee=connected")
