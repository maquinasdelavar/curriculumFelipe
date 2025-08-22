import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings
from app.db import Base, engine
from app.routes import api_router
from app.ui import router as ui_router


def create_app() -> FastAPI:
	app = FastAPI(title=settings.app_name)

	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	app.include_router(api_router)
	app.include_router(ui_router)

	@app.on_event("startup")
	async def on_startup() -> None:
		async with engine.begin() as conn:
			await conn.run_sync(Base.metadata.create_all)

	@app.get("/health")
	async def health() -> dict[str, str]:
		return {"status": "ok"}

	return app


app = create_app()

# To run: uvicorn app.main:app --reload