from pydantic import BaseModel


class AdminDashboardStats(BaseModel):
    total_users: int
    total_tasks: int
    total_tasks_pending: int
    total_tasks_completed: int
