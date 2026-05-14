from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4, UUID
from toan_socratic.db.database import get_db
from toan_socratic.db.models import User, UserRole
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["users"])

class UserCreate(BaseModel):
    email: str
    name: str
    avatar_url: str = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    created_at: str

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_or_get_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user or get existing user by email"""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalars().first()

    if existing_user:
        return {
            "id": str(existing_user.id),
            "email": existing_user.email,
            "name": existing_user.name,
            "role": existing_user.role.value,
            "created_at": existing_user.created_at.isoformat()
        }

    # Create new user
    new_user = User(
        id=uuid4(),
        email=user_data.email,
        name=user_data.name,
        role=UserRole.STUDENT
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "name": new_user.name,
        "role": new_user.role.value,
        "created_at": new_user.created_at.isoformat()
    }

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user by ID"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "created_at": user.created_at.isoformat()
    }
