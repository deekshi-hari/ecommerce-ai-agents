from pydantic import BaseModel, Field
from typing import Optional, List

class ProductIn(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    color: Optional[str] = None
    size: Optional[str] = None
    product_type: Optional[str] = Field(None)

class ProductOut(ProductIn):
    id: int
    class Config:
        from_attributes = True

class CartAdd(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductOut
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    session_id: str
    total: float
    class Config:
        from_attributes = True

class CheckoutOut(BaseModel):
    status: str
    payment_link: Optional[str] = None
    amount: Optional[float] = None
    message: Optional[str] = None
