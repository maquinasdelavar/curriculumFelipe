from fastapi import APIRouter

from app.routers import auth as auth_router
from app.routers import parts as parts_router
from app.routers import suppliers as suppliers_router
from app.routers import customers as customers_router
from app.routers import transactions as transactions_router


api_router = APIRouter()
api_router.include_router(auth_router.router)
api_router.include_router(parts_router.router)
api_router.include_router(suppliers_router.router)
api_router.include_router(customers_router.router)
api_router.include_router(transactions_router.router)