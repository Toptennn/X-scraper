from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    user_obj = models.User(
        username=user.username,
        hashed_password=auth.get_password_hash(user.password),
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token}


@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user_obj = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user_obj or not auth.verify_password(form_data.password, user_obj.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = auth.create_access_token({"sub": user_obj.username})
    return {"access_token": token}
