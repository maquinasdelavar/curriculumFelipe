from typing import Optional, List

from fastapi import APIRouter, Depends, Query, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import authenticate_user, create_access_token
from app.db import get_db_session
from app.models import Part, StockMovement, StockMovementType


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)


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


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
	return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/ui/login", response_class=HTMLResponse)
async def ui_login_get(request: Request):
	return templates.TemplateResponse("login.html", {"request": request, "token": None, "error": None})


@router.post("/ui/login", response_class=HTMLResponse)
async def ui_login_post(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	session: AsyncSession = Depends(get_db_session),
):
	user = await authenticate_user(session, username, password)
	if not user:
		return templates.TemplateResponse("login.html", {"request": request, "token": None, "error": "Credenciais inválidas"})
	token = create_access_token({"sub": user.username})
	return templates.TemplateResponse("login.html", {"request": request, "token": token, "error": None})


@router.get("/ui/parts", response_class=HTMLResponse)
async def ui_parts_list(
	request: Request,
	q: Optional[str] = Query(None),
	session: AsyncSession = Depends(get_db_session),
):
	stmt = select(Part)
	if q:
		stmt = stmt.where((Part.sku.ilike(f"%{q}%")) | (Part.name.ilike(f"%{q}%")))
	result = await session.execute(stmt.order_by(Part.name.asc()))
	parts = result.scalars().all()
	rows: List[dict] = []
	for p in parts:
		rows.append(
			{
				"id": p.id,
				"sku": p.sku,
				"name": p.name,
				"sale_price": float(p.sale_price or 0),
				"stock": await get_stock(session, p.id),
			}
		)
	return templates.TemplateResponse("parts_list.html", {"request": request, "parts": rows, "q": q})