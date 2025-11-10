from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """
    Camada de acesso a dados (Repositório) para o modelo User.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtém um utilizador ATIVO pelo seu email.
        Implementa a regra de soft delete.
        """
        return (
            self.db.query(User)
            .filter(User.email == email)
            .filter(User.deleted_at.is_(None))  # <- AQUI é is_(None), não "is None"
            .first()
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtém um utilizador ATIVO pelo seu ID.
        """
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .filter(User.deleted_at.is_(None))
            .first()
        )

    def create(self, user_create: UserCreate, hashed_password: str) -> User:
        """
        Cria um novo utilizador.
        NÃO faz commit aqui — isso é responsabilidade do service.
        """
        new_user = User(email=user_create.email, hashed_password=hashed_password)
        self.db.add(new_user)
        return new_user
