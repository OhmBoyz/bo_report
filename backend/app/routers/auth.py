from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer



from app import crud, schemas
from app.services import auth_service
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserRead)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = auth_service.hash_password(user_in.password)
    user = crud.create_user(db, user_in.username, hashed)
    return user

@router.post("/token")
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth_service.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

