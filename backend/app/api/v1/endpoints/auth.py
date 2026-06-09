from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register(db, payload)


@router.post('/login', response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    access_token = AuthService.login(db, payload.email, payload.password)
    return Token(access_token=access_token)
