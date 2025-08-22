import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_password_hash
from app.db import Base, engine, AsyncSessionLocal
from app.models import User, Category, Brand, Part


async def seed() -> None:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

	async with AsyncSessionLocal() as session:  # type: AsyncSession
		# Admin user
		res = await session.execute(select(User).where(User.username == "admin"))
		admin = res.scalar_one_or_none()
		if not admin:
			admin = User(username="admin", hashed_password=get_password_hash("admin"), is_admin=True)
			session.add(admin)

		# Category and brand
		cat = await session.execute(select(Category).where(Category.name == "Motor"))
		cat = cat.scalar_one_or_none() or Category(name="Motor")
		if cat.id is None:
			session.add(cat)
		brand = await session.execute(select(Brand).where(Brand.name == "Genérica"))
		brand = brand.scalar_one_or_none() or Brand(name="Genérica")
		if brand.id is None:
			session.add(brand)

		await session.flush()

		# Parts
		res = await session.execute(select(Part).where(Part.sku == "FILTRO-001"))
		if not res.scalar_one_or_none():
			p = Part(sku="FILTRO-001", name="Filtro de Óleo", category_id=cat.id, brand_id=brand.id, cost_price=20.0, sale_price=39.9, min_stock=2)
			session.add(p)

		await session.commit()


async def main() -> None:
	await seed()


if __name__ == "__main__":
	asyncio.run(main())