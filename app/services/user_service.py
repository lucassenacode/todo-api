# app/services/user_service.py
from fastapi import HTTPException, status
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
    """
    Camada de Serviço (Regras de Negócio) para Utilizadores.
    ...
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
        ...
        """
        # ... (código de registo existente, sem alteração)
        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed_pass = hash_password(user_create.password)
        new_user = self.user_repo.create(user_create, hashed_pass)
        return new_user

    def login_user(self, email: str, password: str) -> Token:
        """
        Orquestra o login do utilizador.

        1. Valida as credenciais (RN-02).
        2. Gera os tokens (RN-03).
        """

        # 1. Encontra o utilizador (apenas utilizadores ativos)
        user = self.user_repo.get_by_email(email)

        # 2. RN-02: Valida a password
        # (Se o utilizador não existir ou a password estiver errada,
        # retorna 401. Não dizemos ao cliente *qual* falhou, por segurança)
        if not user or not verify_password(password, user.hashed_password):
            # Erro 401 Unauthorized, conforme Especificação
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                # Adiciona o header standard para desafios WWW-Authenticate
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. RN-03: Gera os tokens JWT
        # O "sub" (subject) do token é o ID do utilizador
        jwt_data = {"sub": str(user.id)}

        access_token = create_access_token(data=jwt_data)
        refresh_token = create_refresh_token(data=jwt_data)

        # Retorna o schema Token
        return Token(access_token=access_token, refresh_token=refresh_token)
