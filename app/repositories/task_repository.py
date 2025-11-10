from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self, owner_id: int):
        return self.db.query(Task).filter(
            Task.owner_id == owner_id,
            Task.deleted_at.is_(None),
        )

    def get_by_id(self, task_id: int, owner_id: int) -> Optional[Task]:
        return self._base_query(owner_id).filter(Task.id == task_id).first()

    def list(
        self, owner_id: int, status: Optional[TaskStatus], limit: int, offset: int
    ) -> Tuple[List[Task], int]:
        query = self._base_query(owner_id)

        if status:
            query = query.filter(Task.status == status)

        total = query.count()
        tasks = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()
        return tasks, total

    def create(
        self, task_create: TaskCreate, owner_id: int, status: TaskStatus
    ) -> Task:
        new_task = Task(
            **task_create.model_dump(),
            owner_id=owner_id,
            status=status,
        )
        self.db.add(new_task)
        return new_task

    def update(self, db_task: Task, task_update: TaskUpdate) -> Task:
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        self.db.add(db_task)
        return db_task

    def delete(self, db_task: Task) -> None:
        db_task.deleted_at = func.now()
        self.db.add(db_task)

    # --- usados pelo dashboard admin ---

    def count_all_active(self) -> int:
        return self.db.query(Task).filter(Task.deleted_at.is_(None)).count()

    def count_by_status(self, status: TaskStatus) -> int:
        return (
            self.db.query(Task)
            .filter(Task.deleted_at.is_(None), Task.status == status)
            .count()
        )
