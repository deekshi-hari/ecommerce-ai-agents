from fastapi import FastAPI
from .routers import products, cart, orders
from .db import engine, Base

app = FastAPI(title="Ecommerce API")

# Routers
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
