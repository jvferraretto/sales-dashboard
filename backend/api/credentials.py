from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Platform, PlatformCredential
from schemas import CredentialStatus

router = APIRouter()


@router.get("", response_model=Dict[str, CredentialStatus])
def get_credentials(db: Session = Depends(get_db)):
    result = {}
    for p in [Platform.MELI, Platform.SHOPEE]:
        cred = db.query(PlatformCredential).filter_by(platform=p).first()
        if cred and cred.access_token:
            result[p.value] = CredentialStatus(
                connected=True,
                seller_id=cred.seller_id,
                shop_id=cred.shop_id,
                expires_at=cred.expires_at,
            )
        else:
            result[p.value] = CredentialStatus(connected=False)
    return result
