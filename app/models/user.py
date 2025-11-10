# app/models/user.py
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base  # Importamos nossa Base declarative


class User(Base):
    """
    Modelo de dados para a tabela 'users'.
    Adiciona os campos 'name' e 'role' (para admin).
    """

    # Nome da tabela no banco de dados
    __tablename__ = "users"

    # Colunas (conforme Especificação de Produto)
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    name = Column(String(255), nullable=True)

    role = Column(String(50), nullable=False, server_default="user", index=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime, nullable=True, index=True)
