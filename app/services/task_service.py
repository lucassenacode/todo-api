# app/services/task_service.py
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskList, TaskStatus, TaskUpdate


class TaskService:
    """
    Camada de Serviço (Regras de Negócio) para Tarefas (Tasks).

    Orquestra as operações, aplica a lógica de negócio e coordena
    o repositório de tarefas.
    """

    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)

    def _get_task_by_id_and_owner(self, task_id: int, owner_id: int) -> Task:
        """
        Função helper para obter uma tarefa e validar o "ownership".
        Implementa a RN-05.
        """
        db_task = self.task_repo.get_by_id(task_id, owner_id)

        # RN-05: Se a tarefa não existir ou não pertencer ao utilizador,
        # retorna 404 Not Found.
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return db_task

    def create_task(self, task_create: TaskCreate, owner_id: int) -> Task:
        """
        Orquestra a criação de uma nova tarefa.
        """

        # RN-06: Ao criar uma nova tarefa, o status padrão
        # deve ser sempre 'pending'.
        new_task = self.task_repo.create(
            task_create=task_create,
            owner_id=owner_id,
            status=TaskStatus.PENDING,  # Define o status padrão
        )
        return new_task

    def list_tasks(
        self,
        owner_id: int,
        status_filter: Optional[TaskStatus],
        limit: int,
        offset: int,
    ) -> TaskList:
        """
        Lista as tarefas de um utilizador, aplicando filtros e paginação.
        """
        tasks, total = self.task_repo.list(
            owner_id=owner_id, status=status_filter, limit=limit, offset=offset
        )

        # Retorna o schema TaskList, conforme Especificação
        return TaskList(items=tasks, total=total)

    def get_task(self, task_id: int, owner_id: int) -> Task:
        """
        Obtém os detalhes de uma tarefa específica.
        """
        # A validação de ownership (RN-05) é tratada pela função helper
        return self._get_task_by_id_and_owner(task_id, owner_id)

    def update_task(self, task_id: int, task_update: TaskUpdate, owner_id: int) -> Task:
        """
        Atualiza uma tarefa.
        """
        # 1. Valida o ownership (RN-05)
        db_task = self._get_task_by_id_and_owner(task_id, owner_id)

        # 2. RN-07: Apenas title, description e status podem ser atualizados.
        # (O nosso schema TaskUpdate já garante isto).

        # 3. Chama o repositório para aplicar as atualizações
        updated_task = self.task_repo.update(db_task=db_task, task_update=task_update)
        return updated_task

    def delete_task(self, task_id: int, owner_id: int) -> None:
        """
        Apaga uma tarefa (soft delete).
        """
        # 1. Valida o ownership (RN-05)
        db_task = self._get_task_by_id_and_owner(task_id, owner_id)

        # 2. Chama o repositório para fazer o soft delete
        self.task_repo.delete(db_task)
