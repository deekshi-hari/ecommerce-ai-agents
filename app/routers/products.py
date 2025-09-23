from fastapi import APIRouter, Depends, HTTPException
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
async def list_products(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(models.Product))
    return res.scalars().all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_session)):
    product = await db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product
