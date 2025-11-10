from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.security.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_create: UserCreate) -> User:
        # 1. Verifica se já existe (regra normal)
        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed_pass = hash_password(user_create.password)

        try:
            # 2. Cria o user e faz commit aqui
            new_user = self.user_repo.create(user_create, hashed_pass)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user

        except IntegrityError:
            # 3. Se outra request criou ao mesmo tempo (race condition), converte em 409
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    def login_user(self, email: str, password: str) -> Token:
        user = self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        jwt_data = {"sub": str(user.id)}
        access_token = create_access_token(data=jwt_data)
        refresh_token = create_refresh_token(data=jwt_data)

        return Token(access_token=access_token, refresh_token=refresh_token)
