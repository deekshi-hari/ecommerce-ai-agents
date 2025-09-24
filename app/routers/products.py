from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import models, schemas

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=schemas.ProductOut, status_code=201)
async def create_product(payload: schemas.ProductIn, db: AsyncSession = Depends(get_session)):
    product = models.Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.get("", response_model=list[schemas.ProductOut])
async def list_products(
    color: str | None = Query(None),
    product_type: str | None = Query(None),
    size: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
):
    stmt = select(models.Product)

    if color:
        stmt = stmt.where(models.Product.color == color)
    if product_type:
        stmt = stmt.where(models.Product.product_type == product_type)
    if size:
        stmt = stmt.where(models.Product.size == size)

    stmt = stmt.order_by(models.Product.id.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_session)):
    product = await db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product
