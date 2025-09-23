from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import models, schemas

router = APIRouter(prefix="/cart", tags=["cart"])

def session_header_or_default(x_session_id: str | None) -> str:
    return x_session_id or "demo-session"  # replace with real session/user later

@router.post("/add", response_model=schemas.CartItemOut)
async def add_to_cart(
    item: schemas.CartAdd,
    db: AsyncSession = Depends(get_session),
    x_session_id: str | None = Header(default=None)
):
    session_id = session_header_or_default(x_session_id)
    product = await db.get(models.Product, item.product_id)
    if not product or product.stock < item.quantity:
        raise HTTPException(400, "Product not available / insufficient stock")

    ci = models.CartItem(session_id=session_id, product_id=item.product_id, quantity=item.quantity)
    db.add(ci)
    await db.commit()
    await db.refresh(ci)
    return ci

@router.get("", response_model=list[schemas.CartItemOut])
async def view_cart(db: AsyncSession = Depends(get_session), x_session_id: str | None = Header(default=None)):
    session_id = session_header_or_default(x_session_id)
    q = select(models.CartItem).where(models.CartItem.session_id == session_id)
    res = await db.execute(q)
    return res.scalars().all()

@router.post("/checkout", response_model=schemas.OrderOut)
async def checkout(db: AsyncSession = Depends(get_session), x_session_id: str | None = Header(default=None)):
    session_id = session_header_or_default(x_session_id)

    # fetch cart with products
    q = select(models.CartItem).where(models.CartItem.session_id == session_id)
    res = await db.execute(q)
    items = res.scalars().all()
    if not items:
        raise HTTPException(400, "Cart is empty")

    # compute total & validate stock
    total = 0
    for it in items:
        prod = await db.get(models.Product, it.product_id, with_for_update=True)
        if prod.stock < it.quantity:
            raise HTTPException(400, f"Insufficient stock for product {prod.id}")
        total += float(prod.price) * it.quantity
        prod.stock -= it.quantity

    order = models.Order(session_id=session_id, total=total)
    db.add(order)
    await db.flush()  # get order.id

    for it in items:
        prod = await db.get(models.Product, it.product_id)
        db.add(models.OrderItem(
            order_id=order.id, product_id=it.product_id,
            quantity=it.quantity, price_each=float(prod.price)
        ))

    # clear cart
    await db.execute(
        models.CartItem.__table__.delete().where(models.CartItem.session_id == session_id)
    )

    await db.commit()
    await db.refresh(order)
    return order
