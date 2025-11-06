# app/security/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

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
