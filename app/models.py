from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    func,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class StockMovementType(str, Enum):
    INCOMING = "IN"
    OUTGOING = "OUT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    purchases: Mapped[List[Purchase]] = relationship(back_populates="user")  # type: ignore  # noqa: F821
    sales: Mapped[List[Sale]] = relationship(back_populates="user")  # type: ignore  # noqa: F821


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    parts: Mapped[List[Part]] = relationship(back_populates="category")  # type: ignore  # noqa: F821


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    parts: Mapped[List[Part]] = relationship(back_populates="brand")  # type: ignore  # noqa: F821


class Part(Base):
    __tablename__ = "parts"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_parts_sku"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), index=True)
    brand_id: Mapped[Optional[int]] = mapped_column(ForeignKey("brands.id"), index=True)
    cost_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    sale_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category: Mapped[Optional[Category]] = relationship(back_populates="parts")  # type: ignore  # noqa: F821
    brand: Mapped[Optional[Brand]] = relationship(back_populates="parts")  # type: ignore  # noqa: F821
    purchase_items: Mapped[List[PurchaseItem]] = relationship(back_populates="part")  # type: ignore  # noqa: F821
    sale_items: Mapped[List[SaleItem]] = relationship(back_populates="part")  # type: ignore  # noqa: F821
    movements: Mapped[List[StockMovement]] = relationship(back_populates="part")  # type: ignore  # noqa: F821


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(64))

    purchases: Mapped[List[Purchase]] = relationship(back_populates="supplier")  # type: ignore  # noqa: F821


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(64))

    sales: Mapped[List[Sale]] = relationship(back_populates="customer")  # type: ignore  # noqa: F821


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    note: Mapped[Optional[str]] = mapped_column(Text)

    supplier: Mapped[Supplier] = relationship(back_populates="purchases")  # type: ignore  # noqa: F821
    user: Mapped[User] = relationship(back_populates="purchases")  # type: ignore  # noqa: F821
    items: Mapped[List[PurchaseItem]] = relationship(back_populates="purchase")  # type: ignore  # noqa: F821


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"), index=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2))
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2))

    purchase: Mapped[Purchase] = relationship(back_populates="items")  # type: ignore  # noqa: F821
    part: Mapped[Part] = relationship(back_populates="purchase_items")  # type: ignore  # noqa: F821


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    note: Mapped[Optional[str]] = mapped_column(Text)

    customer: Mapped[Customer] = relationship(back_populates="sales")  # type: ignore  # noqa: F821
    user: Mapped[User] = relationship(back_populates="sales")  # type: ignore  # noqa: F821
    items: Mapped[List[SaleItem]] = relationship(back_populates="sale")  # type: ignore  # noqa: F821


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    total_price: Mapped[float] = mapped_column(Numeric(12, 2))

    sale: Mapped[Sale] = relationship(back_populates="items")  # type: ignore  # noqa: F821
    part: Mapped[Part] = relationship(back_populates="sale_items")  # type: ignore  # noqa: F821


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)
    movement_type: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[int] = mapped_column(Integer)
    ref_type: Mapped[Optional[str]] = mapped_column(String(20))
    ref_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    note: Mapped[Optional[str]] = mapped_column(Text)

    part: Mapped[Part] = relationship(back_populates="movements")  # type: ignore  # noqa: F821