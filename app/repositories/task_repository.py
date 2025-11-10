from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_create: TaskCreate,
        owner_id: int,
        status: TaskStatus,
    ) -> Task:
        task = Task(
            title=task_create.title,
            description=task_create.description,
            owner_id=owner_id,
            status=status.value if hasattr(status, "value") else status,
        )
        self.db.add(task)
        # commit é responsabilidade do service
        return task

    def list(
        self,
        owner_id: int,
        status: Optional[TaskStatus],
        limit: int,
        offset: int,
    ) -> Tuple[List[Task], int]:
        query = (
            self.db.query(Task)
            .filter(Task.owner_id == owner_id)
            .filter(Task.deleted_at.is_(None))
        )

        if status is not None:
            query = query.filter(
                Task.status == (status.value if hasattr(status, "value") else status)
            )

        total = query.count()

        items = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

        return items, total

    def get_by_id(self, task_id: int, owner_id: int) -> Optional[Task]:
        return (
            self.db.query(Task)
            .filter(
                Task.id == task_id,
                Task.owner_id == owner_id,
                Task.deleted_at.is_(None),
            )
            .first()
        )

    def update(self, db_task: Task, task_update: TaskUpdate) -> Task:
        if task_update.title is not None:
            db_task.title = task_update.title
        if task_update.description is not None:
            db_task.description = task_update.description
        if task_update.status is not None:
            db_task.status = (
                task_update.status.value
                if hasattr(task_update.status, "value")
                else task_update.status
            )

        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete(self, db_task: Task) -> None:
        db_task.deleted_at = func.now()
        self.db.commit()
