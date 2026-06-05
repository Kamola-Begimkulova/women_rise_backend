"""Auth router — register, login, current user. TO BE IMPLEMENTED.

Endpoints (paths already prefixed with /api/auth):
  POST   /api/auth/register  body=UserCreate  -> Token
  POST   /api/auth/login     body=UserLogin   -> Token
  GET    /api/auth/me        (auth)           -> UserOut
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(body: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = models.User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        bio=body.bio,
        expertise=body.expertise,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return schemas.Token(access_token=token, token_type="bearer", user=user)


@router.post("/login", response_model=schemas.Token)
def login(body: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id)
    return schemas.Token(access_token=token, token_type="bearer", user=user)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
