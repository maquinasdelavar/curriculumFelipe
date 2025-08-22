from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db_session
from app.models import Part, StockMovement, StockMovementType
from app.schemas import PartCreate, PartOut, PartUpdate


router = APIRouter(prefix="/parts", tags=["parts"])


async def get_stock(session: AsyncSession, part_id: int) -> int:
    incoming_q = select(func.coalesce(func.sum(StockMovement.quantity), 0)).where(
        StockMovement.part_id == part_id, StockMovement.movement_type == StockMovementType.INCOMING.value
    )
    outgoing_q = select(func.coalesce(func.sum(StockMovement.quantity), 0)).where(
        StockMovement.part_id == part_id, StockMovement.movement_type == StockMovementType.OUTGOING.value
    )
    res_in = await session.execute(incoming_q)
    res_out = await session.execute(outgoing_q)
    return int(res_in.scalar_one() - res_out.scalar_one())


@router.get("/", response_model=List[PartOut])
async def list_parts(
    q: Optional[str] = Query(None, description="Search by sku or name"),
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    stmt = select(Part)
    if q:
        stmt = stmt.where((Part.sku.ilike(f"%{q}%")) | (Part.name.ilike(f"%{q}%")))
    result = await session.execute(stmt.order_by(Part.name.asc()))
    parts = result.scalars().all()
    out: List[PartOut] = []
    for p in parts:
        stock = await get_stock(session, p.id)
        out.append(
            PartOut(
                id=p.id,
                sku=p.sku,
                name=p.name,
                category_id=p.category_id,
                brand_id=p.brand_id,
                cost_price=float(p.cost_price or 0),
                sale_price=float(p.sale_price or 0),
                min_stock=p.min_stock,
                created_at=p.created_at,
                stock=stock,
            )
        )
    return out


@router.post("/", response_model=PartOut)
async def create_part(payload: PartCreate, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    part = Part(**payload.model_dump())
    session.add(part)
    await session.commit()
    await session.refresh(part)
    stock = await get_stock(session, part.id)
    return PartOut(**PartOut.model_validate(part).model_dump(), stock=stock)


@router.get("/{part_id}", response_model=PartOut)
async def get_part(part_id: int, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    part = await session.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    stock = await get_stock(session, part.id)
    return PartOut(**PartOut.model_validate(part).model_dump(), stock=stock)


@router.put("/{part_id}", response_model=PartOut)
async def update_part(
    part_id: int,
    payload: PartUpdate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    part = await session.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(part, k, v)
    await session.commit()
    await session.refresh(part)
    stock = await get_stock(session, part.id)
    return PartOut(**PartOut.model_validate(part).model_dump(), stock=stock)


@router.delete("/{part_id}")
async def delete_part(part_id: int, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    part = await session.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    await session.delete(part)
    await session.commit()
    return {"ok": True}