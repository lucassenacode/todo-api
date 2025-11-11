from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserProfileUpdate
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
        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed_pass = hash_password(user_create.password)

        try:
            new_user = self.user_repo.create(user_create, hashed_pass)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except IntegrityError:
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

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def get_current_profile(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    def update_own_profile(
        self,
        user: User,
        profile_data: UserProfileUpdate,
    ) -> User:
        updated_user = self.user_repo.update_profile(user, profile_data)

        if profile_data.new_password:
            updated_user.hashed_password = hash_password(
                profile_data.new_password,
            )

        self.db.add(updated_user)
        self.db.commit()
        self.db.refresh(updated_user)

        return updated_user

    def delete_own_account(self, user: User) -> None:
        self.user_repo.soft_delete(user)
        self.db.commit()
