# app/models/task.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Task(Base):
    """
    Modelo de dados para a tabela 'tasks'.

    Define a estrutura da tabela de tarefas, incluindo a chave estrangeira (FK)
    para o 'owner_id' que a liga ao utilizador (User).
    """

    __tablename__ = "tasks"

    # Colunas (conforme Especificação de Produto)
    id = Column(Integer, primary_key=True, index=True)

    # Chave estrangeira que garante o "ownership"
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # 'Text' para descrições longas

    status = Column(String(50), nullable=False, index=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    deleted_at = Column(DateTime, nullable=True, index=True)
