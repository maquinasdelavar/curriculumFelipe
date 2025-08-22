from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import authenticate_user, create_access_token, get_password_hash
from app.core.config import settings
from app.db import get_db_session
from app.models import User
from app.schemas import Token, UserCreate, UserOut


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut)
async def register_user(payload: UserCreate, session: AsyncSession = Depends(get_db_session)):
    # prevent duplicates
    existing = await session.execute(
        User.__table__.select().where(User.username == payload.username)  # type: ignore
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        is_admin=payload.is_admin,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user