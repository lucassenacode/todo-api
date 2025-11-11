from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskRead(TaskBase):
    id: int
    owner_id: int
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    items: List[TaskRead]
    total: int
