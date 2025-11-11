from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.user import User
from app.schemas.admin import AdminDashboardStats
from app.security.auth import get_current_user
from app.services.admin_service import AdminService

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


def get_admin_service(db: Session = Depends(get_db_session)) -> AdminService:
    return AdminService(db)


def ensure_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/dashboard", response_model=AdminDashboardStats)
def get_admin_dashboard(
    _: User = Depends(ensure_admin),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Retorna estatísticas do dashboard administrativo."""
    return admin_service.get_dashboard_stats()
