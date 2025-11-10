# app/repositories/task_repository.py
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate


class TaskRepository:
    """
    Camada de acesso a dados (Repositório) para o modelo Task.

    Implementa as operações de base de dados (CRUD) para tarefas,
    garantindo sempre o "ownership" (isolamento por utilizador).
    """

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self, owner_id: int):
        """
        Query base que aplica as regras de "ownership" e "soft delete".
        Todas as outras consultas devem usar esta como base.
        """
        return self.db.query(Task).filter(
            Task.owner_id == owner_id, Task.deleted_at is None
        )

    def get_by_id(self, task_id: int, owner_id: int) -> Optional[Task]:
        """
        Obtém uma tarefa específica, verificando o "ownership".
        Implementa a RN-04.
        """
        return self._base_query(owner_id).filter(Task.id == task_id).first()

    def list(
        self, owner_id: int, status: Optional[TaskStatus], limit: int, offset: int
    ) -> (List[Task], int):
        """
        Lista as tarefas de um utilizador com filtros e paginação.
        Implementa o GET /api/v1/tasks.
        """
        query = self._base_query(owner_id)

        # Aplica o filtro de status, se fornecido
        if status:
            query = query.filter(Task.status == status)

        # Conta o total de itens *antes* de aplicar a paginação
        total = query.count()

        # Aplica ordenação (mais recentes primeiro) e paginação
        tasks = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()

        return tasks, total

    def create(
        self, task_create: TaskCreate, owner_id: int, status: TaskStatus
    ) -> Task:
        """
        Cria uma nova tarefa.
        O owner_id e o status são fornecidos pelo Service (RN-06).
        """
        new_task = Task(
            **task_create.model_dump(),  # title e description
            owner_id=owner_id,
            status=status,
        )

        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def update(self, db_task: Task, task_update: TaskUpdate) -> Task:
        """
        Atualiza uma tarefa existente.
        Recebe a tarefa (db_task) já validada pelo Service.
        """
        # Obtém os dados do schema, excluindo os que não foram definidos
        update_data = task_update.model_dump(exclude_unset=True)

        # Atualiza o objeto do modelo
        for key, value in update_data.items():
            setattr(db_task, key, value)

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete(self, db_task: Task) -> None:
        """
        "Apaga" uma tarefa (soft delete).
        Recebe a tarefa (db_task) já validada pelo Service.
        """
        # self.db.delete(db_task) <-- Isto seria um HARD delete

        # Implementação do Soft Delete:
        db_task.deleted_at = func.now()
        self.db.add(db_task)
        self.db.commit()
