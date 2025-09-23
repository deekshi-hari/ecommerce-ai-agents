# scripts/seed_products.py
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Product

SEED = [
    {"name": "Blue T-Shirt", "price": 499.00, "stock": 25, "description": "Cotton, regular fit"},
    {"name": "Black Jeans",    "price": 1599.00, "stock": 15, "description": "Slim fit denim"},
    {"name": "Adidas Running Shoes", "price": 2999.00, "stock": 10, "description": "Can be used in GYM and Any sports"},
]

async def main():
    async with async_session_maker() as session:
        # idempotent insert: skip if name exists
        for p in SEED:
            exists = await session.scalar(select(Product).where(Product.name == p["name"]))
            if not exists:
                session.add(Product(**p))
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
