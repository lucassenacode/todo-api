# app/repositories/user_repository.py
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """
    Camada de acesso a dados (Repositório) para o modelo User.

    Implementa as operações de base de dados (CRUD) para utilizadores.
    """

    def __init__(self, db: Session):
        """
        Inicializa o repositório com uma sessão de base de dados.

        Args:
            db (Session): A sessão do SQLAlchemy a ser usada.
        """
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtém um utilizador ATIVO pelo seu email.

        Implementa a regra de soft delete (apenas utilizadores não apagados).
        """
        return (
            self.db.query(User)
            .filter(User.email == email, User.deleted_at == None)
            .first()
        )

    def create(self, user_create: UserCreate, hashed_password: str) -> User:
        """
        Cria um novo registo de utilizador na base de dados.

        Nota: A password já deve vir "hasheada" do service.
        """
        # Cria a nova instância do modelo SQLAlchemy
        new_user = User(email=user_create.email, hashed_password=hashed_password)

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)  # Atualiza o objeto new_user com dados do DB (ex: ID)

        return new_user
