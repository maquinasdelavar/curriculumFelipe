from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db_session
from app.models import Supplier
from app.schemas import SupplierCreate, SupplierOut


router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("/", response_model=List[SupplierOut])
async def list_suppliers(session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    result = await session.execute(select(Supplier).order_by(Supplier.name.asc()))
    return result.scalars().all()


@router.post("/", response_model=SupplierOut)
async def create_supplier(payload: SupplierCreate, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    supplier = Supplier(**payload.model_dump())
    session.add(supplier)
    await session.commit()
    await session.refresh(supplier)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierOut)
async def get_supplier(supplier_id: int, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    supplier = await session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.put("/{supplier_id}", response_model=SupplierOut)
async def update_supplier(supplier_id: int, payload: SupplierCreate, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    supplier = await session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(supplier, k, v)
    await session.commit()
    await session.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: int, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    supplier = await session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    await session.delete(supplier)
    await session.commit()
    return {"ok": True}