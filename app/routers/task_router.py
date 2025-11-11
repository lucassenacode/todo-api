from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.user import User
from app.schemas.task import TaskCreate, TaskList, TaskRead, TaskStatus, TaskUpdate
from app.security.auth import get_current_user
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
    dependencies=[Depends(get_current_user)],
)


def get_task_service(db: Session = Depends(get_db_session)) -> TaskService:
    return TaskService(db)


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_create: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Cria uma tarefa associada ao usuário autenticado."""
    return task_service.create_task(
        task_create=task_create,
        owner_id=current_user.id,
    )


@router.get(
    "/",
    response_model=TaskList,
)
def list_tasks(
    status_filter: Optional[TaskStatus] = None,
    limit: int = 25,
    offset: int = 0,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Lista tarefas do usuário autenticado, com filtro por status e paginação."""
    return task_service.list_tasks(
        owner_id=current_user.id,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
)
def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Obtém detalhes de uma tarefa do usuário autenticado."""
    return task_service.get_task(
        task_id=task_id,
        owner_id=current_user.id,
    )


@router.put(
    "/{task_id}",
    response_model=TaskRead,
)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Atualiza uma tarefa do usuário autenticado."""
    return task_service.update_task(
        task_id=task_id,
        task_update=task_update,
        owner_id=current_user.id,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Soft delete de uma tarefa do usuário autenticado."""
    task_service.delete_task(
        task_id=task_id,
        owner_id=current_user.id,
    )
    return None
