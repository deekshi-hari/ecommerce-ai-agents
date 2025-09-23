from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])

def session_header_or_default(x_session_id: str | None) -> str:
    return x_session_id or "demo-session"

@router.get("", response_model=list[schemas.OrderOut])
async def list_orders(db: AsyncSession = Depends(get_session), x_session_id: str | None = Header(default=None)):
    session_id = session_header_or_default(x_session_id)
    res = await db.execute(select(models.Order).where(models.Order.session_id == session_id))
    return res.scalars().all()
