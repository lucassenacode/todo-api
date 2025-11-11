from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db_session),
):
    """Registra um novo usuário."""
    user_service = UserService(db)
    return user_service.register_user(user_create)


@router.post(
    "/login",
    response_model=Token,
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
):
    """
    Autentica o usuário e retorna tokens JWT.
    Usa `username` como email.
    """
    user_service = UserService(db)
    return user_service.login_user(
        email=form_data.username,
        password=form_data.password,
    )
