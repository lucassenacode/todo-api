from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.user import User
from app.schemas.user import UserProfileUpdate, UserRead
from app.security.auth import get_current_user
from app.services.user_service import UserService

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


def get_user_service(db: Session = Depends(get_db_session)) -> UserService:
    return UserService(db)


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Devolve o utilizador autenticado.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def update_me(
    profile_data: UserProfileUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    Atualiza o próprio perfil:
    - name
    - new_password (opcional)
    - NÃO altera email
    """
    return user_service.update_own_profile(current_user, profile_data)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_me(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    Soft delete da própria conta.
    """
    user_service.delete_own_account(current_user)
    return None
