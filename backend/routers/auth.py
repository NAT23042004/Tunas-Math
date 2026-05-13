from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from jose import jwt

from config import settings
from db.database import get_db
from db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenRequest(BaseModel):
    user_id: UUID


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=settings.jwt_expiration_hours))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/token", response_model=TokenResponse)
async def generate_token(token_request: TokenRequest, db: AsyncSession = Depends(get_db)):
    """Generate a JWT token for a backend user.

    This is a development bridge used by the server-side NextAuth route.
    It should be replaced with a stronger production auth boundary before deploy.
    """
    result = await db.execute(select(User).where(User.id == token_request.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}
