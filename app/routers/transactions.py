from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db_session
from app.models import (
    Purchase,
    PurchaseItem,
    Sale,
    SaleItem,
    Part,
    StockMovement,
    StockMovementType,
)
from app.schemas import PurchaseCreate, PurchaseOut, SaleCreate, SaleOut


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/purchases", response_model=PurchaseOut)
async def create_purchase(payload: PurchaseCreate, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    purchase = Purchase(supplier_id=payload.supplier_id, user_id=user.id, note=payload.note or None)  # type: ignore[attr-defined]
    session.add(purchase)
    await session.flush()

    total = 0.0
    for item in payload.items:
        part = await session.get(Part, item.part_id)
        if not part:
            raise HTTPException(status_code=400, detail=f"Part {item.part_id} not found")
        total_cost = item.unit_cost * item.quantity
        total += total_cost
        p_item = PurchaseItem(
            purchase_id=purchase.id,
            part_id=part.id,
            quantity=item.quantity,
            unit_cost=item.unit_cost,
            total_cost=total_cost,
        )
        session.add(p_item)
        session.add(
            StockMovement(
                part_id=part.id,
                movement_type=StockMovementType.INCOMING.value,
                quantity=item.quantity,
                ref_type="purchase",
                ref_id=purchase.id,
            )
        )

    purchase.total = total
    await session.commit()
    await session.refresh(purchase)
    return PurchaseOut(id=purchase.id, supplier_id=purchase.supplier_id, total=float(purchase.total or 0))


@router.post("/sales", response_model=SaleOut)
async def create_sale(payload: SaleCreate, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    sale = Sale(customer_id=payload.customer_id, user_id=user.id, note=payload.note or None)  # type: ignore[attr-defined]
    session.add(sale)
    await session.flush()

    total = 0.0
    # Optional: validate stock availability per item
    for item in payload.items:
        part = await session.get(Part, item.part_id)
        if not part:
            raise HTTPException(status_code=400, detail=f"Part {item.part_id} not found")
        total_price = item.unit_price * item.quantity
        total += total_price
        s_item = SaleItem(
            sale_id=sale.id,
            part_id=part.id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=total_price,
        )
        session.add(s_item)
        session.add(
            StockMovement(
                part_id=part.id,
                movement_type=StockMovementType.OUTGOING.value,
                quantity=item.quantity,
                ref_type="sale",
                ref_id=sale.id,
            )
        )

    sale.total = total
    await session.commit()
    await session.refresh(sale)
    return SaleOut(id=sale.id, customer_id=sale.customer_id, total=float(sale.total or 0))