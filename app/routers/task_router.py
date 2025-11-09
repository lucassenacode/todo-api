# app/routers/task_router.py
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.user import User
from app.schemas.task import TaskCreate, TaskList, TaskRead, TaskStatus, TaskUpdate
from app.security.auth import get_current_user
from app.services.task_service import TaskService

# Cria um novo "router" (um mini-app FastAPI)
# Todos os endpoints aqui requerem autenticação (veja 'dependencies')
router = APIRouter(
    prefix="/api/tasks",  # Prefixo da URL (conforme Especificação)
    tags=["Tasks"],  # Tag para a documentação /docs
    # "Tranca" global: Todos os endpoints neste router
    # exigem que a dependência get_current_user seja executada.
    dependencies=[Depends(get_current_user)],
)


# --- Dependência de Serviço ---
# Esta dependência cria o TaskService para nós em cada request,
# já injetando a sessão do DB.
def get_task_service(db: Session = Depends(get_db_session)) -> TaskService:
    return TaskService(db)


# --- Endpoints CRUD de Tarefas ---


@router.post(
    "/",  # Corresponde a POST /api/v1/tasks
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_create: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),  # Obtém o utilizador logado
):
    """
    Cria uma nova tarefa.
    A tarefa é automaticamente associada ao utilizador autenticado (RN-04).
    O status é definido como 'pending' (RN-06).
    """
    return task_service.create_task(task_create=task_create, owner_id=current_user.id)


@router.get(
    "/",  # Corresponde a GET /api/v1/tasks
    response_model=TaskList,
)
def list_tasks(
    status_filter: Optional[TaskStatus] = None,  # Query param ?status=...
    limit: int = 25,
    offset: int = 0,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """
    Lista as tarefas do utilizador autenticado.
    Suporta filtros por status e paginação (limit/offset).
    """
    return task_service.list_tasks(
        owner_id=current_user.id,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{task_id}",  # Corresponde a GET /api/v1/tasks/{task_id}
    response_model=TaskRead,
)
def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém os detalhes de uma tarefa específica.
    Retorna 404 se a tarefa não existir ou não pertencer ao utilizador (RN-05).
    """
    return task_service.get_task(task_id=task_id, owner_id=current_user.id)


@router.put(
    "/{task_id}",  # Corresponde a PUT /api/v1/tasks/{task_id}
    response_model=TaskRead,
)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """
    Atualiza uma tarefa (apenas title, description, status - RN-07).
    Retorna 404 se a tarefa não existir ou não pertencer ao utilizador (RN-05).
    """
    return task_service.update_task(
        task_id=task_id, task_update=task_update, owner_id=current_user.id
    )


@router.delete(
    "/{task_id}",  # Corresponde a DELETE /api/v1/tasks/{task_id}
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """
    Apaga uma tarefa (soft delete).
    Retorna 404 se a tarefa não existir ou não pertencer ao utilizador (RN-05).
    Retorna 204 No Content em caso de sucesso.
    """
    task_service.delete_task(task_id=task_id, owner_id=current_user.id)
    return None  # Retorna uma resposta vazia 204
