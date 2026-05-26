from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from integrations.mercadolivre import exchange_code_for_tokens

router = APIRouter()


@router.get("/login")
def login():
    params = {
        "response_type": "code",
        "client_id": settings.MELI_APP_ID,
        "redirect_uri": settings.MELI_REDIRECT_URI,
    }
    return RedirectResponse(
        f"https://auth.mercadolibre.com.br/authorization?{urlencode(params)}"
    )


@router.get("/callback")
async def callback(code: str, db: Session = Depends(get_db)):
    await exchange_code_for_tokens(db, code)
    return RedirectResponse("http://localhost:3000/settings?meli=connected")
