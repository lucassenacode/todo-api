# app/security/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db_session  # A nossa sessão partilhada
from app.models.user import User  # O modelo de retorno
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
# 1. Configuração do Hashing de Passwords (para RN-02)
# Usa bcrypt como o algoritmo de hashing preferido
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Gera o hash de uma password em texto puro."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a password em texto puro corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)


# 2. Configuração dos Tokens JWT (para RN-03)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um novo Access Token JWT."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Usa o tempo de expiração do .env
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Cria um novo Refresh Token JWT."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica um token, retornando o payload (dados) se for válido.
    Retorna None se o token for inválido ou expirado.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        # Token inválido (expirado, assinatura errada, etc.)
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)
) -> User:
    """
    Dependência de segurança:
    1. Decodifica o token JWT.
    2. Extrai o ID do utilizador ("sub").
    3. Obtém o utilizador da base de dados.
    4. Retorna o objeto User se for válido, senão levanta 401.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        # Se o 'sub' não for um inteiro, o token é inválido
        raise credentials_exception

    # Obtém o utilizador da base de dados
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if user is None:
        # O utilizador não existe ou foi (soft) apagado
        raise credentials_exception

    # Retorna o modelo User completo
    return user
