from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import models, schemas
from uuid import uuid4
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

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

@router.post("/checkout", response_model=schemas.CheckoutOut)
async def checkout(
    request: Request,
    db: AsyncSession = Depends(get_session),
    x_session_id: str | None = Header(default=None),
):
    session_id = session_header_or_default(x_session_id)

    # Load cart lines with product
    res = await db.execute(
        select(models.CartItem)
        .options(selectinload(models.CartItem.product))
        .where(models.CartItem.session_id == session_id)
    )
    items = res.scalars().all()
    if not items:
        return schemas.CheckoutOut(status="empty", message="Cart is empty", amount=0.0)

    # Compute total without changing stock yet
    total = 0.0
    for it in items:
        if not it.product:
            raise HTTPException(400, f"Product {it.product_id} not found")
        total += float(it.product.price) * it.quantity

    token = str(uuid4())
    order = models.Order(
        session_id=session_id,
        total=total,
        status="pending",
        payment_token=token,
    )
    db.add(order)

    await db.flush()
    await db.refresh(order) 

    # Create OrderItems snapshot (price at checkout time)
    for it in items:
        db.add(models.OrderItem(
            order_id=order.id,
            product_id=it.product_id,
            quantity=it.quantity,
            price_each=it.product.price,
        ))

    await db.commit()
    await db.refresh(order)

    # Build payment link pointing to our confirm endpoint
    payment_link = str(request.url_for("payment_confirm", token=token))
    return schemas.CheckoutOut(
        status="pending",
        payment_link=payment_link,
        amount=float(order.total),
        message="Proceed to payment",
    )


@router.get("/pay/{token}", name="payment_confirm")
async def payment_confirm(
    token: str,
    db: AsyncSession = Depends(get_session),
):
    # Find the order by token
    order = await db.scalar(
        select(models.Order).where(models.Order.payment_token == token)
    )
    if not order:
        raise HTTPException(404, "Invalid payment link")

    if order.status == "paid":
        return {"status": "ok", "message": "Payment already completed"}

    # Fetch order items
    oi_res = await db.execute(
        select(models.OrderItem).where(models.OrderItem.order_id == order.id)
    )
    order_items = oi_res.scalars().all()

    # Decrement stock now (simple check)
    for oi in order_items:
        prod = await db.get(models.Product, oi.product_id)
        if not prod:
            raise HTTPException(400, f"Product {oi.product_id} missing")
        if prod.stock < oi.quantity:
            raise HTTPException(409, f"Insufficient stock for product {prod.id}")
        prod.stock -= oi.quantity

    # Mark paid and clear cart for this session
    order.status = "paid"
    await db.execute(
        delete(models.CartItem).where(models.CartItem.session_id == order.session_id)
    )

    await db.commit()
    return {"status": "ok", "message": "Payment successfully completed"}