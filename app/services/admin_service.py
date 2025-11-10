from sqlalchemy.orm import Session

from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import AdminDashboardStats
from app.schemas.task import TaskStatus


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.task_repo = TaskRepository(db)

    def get_dashboard_stats(self) -> AdminDashboardStats:
        total_users = self.user_repo.count_active()
        total_tasks = self.task_repo.count_all_active()
        total_tasks_pending = self.task_repo.count_by_status(TaskStatus.PENDING)
        total_tasks_completed = self.task_repo.count_by_status(TaskStatus.COMPLETED)

        return AdminDashboardStats(
            total_users=total_users,
            total_tasks=total_tasks,
            total_tasks_pending=total_tasks_pending,
            total_tasks_completed=total_tasks_completed,
        )
