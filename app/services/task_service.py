from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskList, TaskStatus, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)

    def _get_task_by_id_and_owner(self, task_id: int, owner_id: int) -> Task:
        task = self.task_repo.get_by_id(task_id=task_id, owner_id=owner_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    def create_task(self, task_create: TaskCreate, owner_id: int) -> Task:
        new_task = self.task_repo.create(
            task_create=task_create,
            owner_id=owner_id,
            status=TaskStatus.PENDING,
        )
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def list_tasks(
        self,
        owner_id: int,
        status_filter: Optional[TaskStatus],
        limit: int,
        offset: int,
    ) -> TaskList:
        tasks, total = self.task_repo.list(
            owner_id=owner_id,
            status=status_filter,
            limit=limit,
            offset=offset,
        )
        return TaskList(items=tasks, total=total)

    def get_task(self, task_id: int, owner_id: int) -> Task:
        return self._get_task_by_id_and_owner(task_id, owner_id)

    def update_task(
        self,
        task_id: int,
        task_update: TaskUpdate,
        owner_id: int,
    ) -> Task:
        db_task = self._get_task_by_id_and_owner(task_id, owner_id)
        updated_task = self.task_repo.update(db_task=db_task, task_update=task_update)
        self.db.commit()
        self.db.refresh(updated_task)
        return updated_task

    def delete_task(self, task_id: int, owner_id: int) -> None:
        db_task = self._get_task_by_id_and_owner(task_id, owner_id)
        self.task_repo.delete(db_task)
        self.db.commit()
