# app/services/user_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.security.auth import hash_password


class UserService:
    """
    Camada de Serviço (Regras de Negócio) para Utilizadores.

    Orquestra as operações, aplica a lógica de negócio e coordena
    as camadas de repositório e segurança.
    """

    def __init__(self, db: Session):
        """
        Inicializa o serviço com uma sessão de DB
        e instancia o repositório.
        """
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_create: UserCreate) -> User:
        """
        Orquestra o registo de um novo utilizador.

        1. Verifica se o email já existe (RN-01).
        2. "Hasheia" a password (RN-02).
        3. Cria o utilizador no repositório.
        """

        # 1. RN-01: O email de um novo usuário deve ser único
        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            # Erro 409 Conflict, conforme Especificação de Produto
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # 2. RN-02: As senhas nunca devem ser salvas em texto puro
        hashed_pass = hash_password(user_create.password)

        # 3. Cria o utilizador
        new_user = self.user_repo.create(user_create, hashed_pass)

        return new_user
