from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True


# Core domain
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class BrandBase(BaseModel):
    name: str


class BrandCreate(BrandBase):
    pass


class BrandOut(BrandBase):
    id: int

    class Config:
        from_attributes = True


class PartBase(BaseModel):
    sku: str
    name: str
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    min_stock: int = 0


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    min_stock: Optional[int] = None


class PartOut(PartBase):
    id: int
    created_at: datetime
    stock: int = 0

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    name: str
    tax_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    id: int

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str
    tax_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int

    class Config:
        from_attributes = True


class PurchaseItemIn(BaseModel):
    part_id: int
    quantity: int = Field(gt=0)
    unit_cost: float = Field(ge=0)


class PurchaseCreate(BaseModel):
    supplier_id: int
    note: Optional[str] = None
    items: List[PurchaseItemIn]


class PurchaseOut(BaseModel):
    id: int
    supplier_id: int
    total: float

    class Config:
        from_attributes = True


class SaleItemIn(BaseModel):
    part_id: int
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)


class SaleCreate(BaseModel):
    customer_id: int
    note: Optional[str] = None
    items: List[SaleItemIn]


class SaleOut(BaseModel):
    id: int
    customer_id: int
    total: float

    class Config:
        from_attributes = True