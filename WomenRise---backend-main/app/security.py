"""Auth utilities: password hashing, JWT creation, current-user dependencies."""
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import config
from .database import get_db
from .models import User

# pbkdf2_sha256 is pure-python — no native bcrypt build needed.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# auto_error=False so we can build an "optional auth" dependency too.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def _decode_user_id(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError):
        return None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Require a valid bearer token; raise 401 otherwise."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc
    user_id = _decode_user_id(token)
    if user_id is None:
        raise credentials_exc
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exc
    return user


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return the user if authenticated, else None (no error)."""
    if not token:
        return None
    user_id = _decode_user_id(token)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()
