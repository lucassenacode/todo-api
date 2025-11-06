# app/models/user.py
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base  # Importamos nossa Base declarative


class User(Base):
    """
    Modelo de dados para a tabela 'users'.

    Esta classe define a estrutura da tabela de usuários no banco de dados,
    incluindo os campos definidos na Especificação de Produto.
    """

    # Nome da tabela no banco de dados
    __tablename__ = "users"

    # Colunas (conforme Especificação de Produto)
    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),  # Define o valor padrão no *servidor* de DB
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),  # Atualiza automaticamente no *servidor* de DB
        nullable=False,
    )

    deleted_at = Column(
        DateTime,
        nullable=True,  # NULO significa que o usuário está ATIVO
        index=True,  # Indexamos para performance (sempre faremos WHERE deleted_at IS NULL)
    )
