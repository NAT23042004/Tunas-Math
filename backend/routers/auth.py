from datetime import datetime, timedelta
from secrets import compare_digest
from typing import Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.database import get_db
from db.models import User, UserRole

router = APIRouter(prefix="/api/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


class TokenRequest(BaseModel):
    user_id: UUID


class GoogleAuthRequest(BaseModel):
    id_token: str


class AuthUserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GoogleAuthResponse(TokenResponse):
    user: AuthUserResponse


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(hours=settings.jwt_expiration_hours)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _serialize_user(user: User) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        avatar_url=user.avatar_url,
    )


def _can_link_existing_email_account(user: User) -> bool:
    return (
        user.role == UserRole.STUDENT
        and user.auth_provider is None
        and user.auth_subject is None
    )


async def verify_google_identity_token(id_token: str) -> dict[str, str]:
    """Validate a Google ID token via Google's tokeninfo endpoint."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google auth is not configured",
        )

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    payload = response.json()
    if payload.get("aud") != settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token audience mismatch",
        )

    if payload.get("email_verified") not in (True, "true"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google email is not verified",
        )

    email = payload.get("email")
    subject = payload.get("sub")
    if not email or not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token missing required claims",
        )

    return {
        "sub": subject,
        "email": email,
        "name": payload.get("name") or email.split("@", 1)[0],
        "picture": payload.get("picture") or "",
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token payload",
        )

    try:
        user_id = UUID(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token subject",
        ) from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.post("/token", response_model=TokenResponse)
async def generate_token(
    token_request: TokenRequest,
    db: AsyncSession = Depends(get_db),
    auth_bridge_secret: str | None = Header(default=None, alias="X-Auth-Bridge-Secret"),
):
    """Generate a JWT token for a backend user."""
    expected_secret = settings.resolved_auth_bridge_secret
    if not auth_bridge_secret or not compare_digest(auth_bridge_secret, expected_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth bridge credentials",
        )

    result = await db.execute(select(User).where(User.id == token_request.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/google", response_model=GoogleAuthResponse)
async def exchange_google_token(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    identity = await verify_google_identity_token(request.id_token)

    result = await db.execute(
        select(User).where(
            User.auth_provider == "google",
            User.auth_subject == identity["sub"],
        )
    )
    user = result.scalars().first()

    if not user:
        result = await db.execute(select(User).where(User.email == identity["email"]))
        user = result.scalars().first()
        if user and not _can_link_existing_email_account(user):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Existing account cannot be linked automatically",
            )

    if user is None:
        user = User(
            email=identity["email"],
            name=identity["name"],
            avatar_url=identity["picture"] or None,
            role=UserRole.STUDENT,
            auth_provider="google",
            auth_subject=identity["sub"],
            last_active=datetime.utcnow(),
        )
        db.add(user)
    else:
        user.name = identity["name"]
        user.avatar_url = identity["picture"] or user.avatar_url
        user.auth_provider = "google"
        user.auth_subject = identity["sub"]
        user.last_active = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _serialize_user(user),
    }
