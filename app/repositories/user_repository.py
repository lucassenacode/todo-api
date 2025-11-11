from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserProfileUpdate


class UserRepository:
    """
    Operações de persistência para usuários.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(
                User.email == email,
                User.deleted_at.is_(None),
            )
            .first()
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
            .first()
        )

    def create(self, user_create: UserCreate, hashed_password: str) -> User:
        new_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        return new_user

    def update_profile(
        self,
        db_user: User,
        profile_data: UserProfileUpdate,
    ) -> User:
        if profile_data.name is not None:
            db_user.name = profile_data.name
        self.db.add(db_user)
        return db_user

    def soft_delete(self, db_user: User) -> None:
        db_user.deleted_at = func.now()
        self.db.add(db_user)

    def list_all(self, limit: int, offset: int) -> Tuple[List[User], int]:
        query = self.db.query(User).filter(User.deleted_at.is_(None))
        total = query.count()
        users = query.offset(offset).limit(limit).all()
        return users, total

    def count_active(self) -> int:
        return self.db.query(User).filter(User.deleted_at.is_(None)).count()
