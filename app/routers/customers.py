from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db_session
from app.models import Customer
from app.schemas import CustomerCreate, CustomerOut


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=List[CustomerOut])
async def list_customers(session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    result = await session.execute(select(Customer).order_by(Customer.name.asc()))
    return result.scalars().all()


@router.post("/", response_model=CustomerOut)
async def create_customer(payload: CustomerCreate, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    customer = Customer(**payload.model_dump())
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: int, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: int, payload: CustomerCreate, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(customer, k, v)
    await session.commit()
    await session.refresh(customer)
    return customer


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, session: AsyncSession = Depends(get_db_session), user=Depends(get_current_user)):
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await session.delete(customer)
    await session.commit()
    return {"ok": True}