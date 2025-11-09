# app/schemas/task.py
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# --- Enum para Status ---
class TaskStatus(str, Enum):
    """
    Define os estados permitidos para uma tarefa,
    conforme Especificação de Produto.
    """

    PENDING = "pending"
    COMPLETED = "completed"


# --- Schemas Base ---
class TaskBase(BaseModel):
    """Schema base para Tarefa, contém campos comuns."""

    title: str
    description: Optional[str] = None


# --- Schemas de API ---


class TaskCreate(TaskBase):
    """
    Schema para a criação de uma nova tarefa (input para POST /tasks).
    A 'Especificação' diz que apenas title e description são enviados.
    O 'owner_id' e 'status' são definidos pela lógica de negócio (Serviço).
    """

    pass  # Herda title e description de TaskBase


class TaskUpdate(BaseModel):
    """
    Schema para a atualização de uma tarefa (input para PUT /tasks/{id}).
    A 'Especificação' (RN-07) diz que apenas estes campos
    podem ser atualizados. Todos são opcionais.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskRead(TaskBase):
    """
    Schema para a leitura de uma tarefa (output dos endpoints).
    Inclui os campos do modelo que são seguros para devolver ao cliente.
    """

    id: int
    owner_id: int
    status: TaskStatus

    # Configuração Pydantic v2 (substitui o 'class Config')
    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    """
    Schema para a listagem de tarefas (output de GET /tasks).
    """

    items: List[TaskRead]
    total: int
