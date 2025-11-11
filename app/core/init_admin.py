import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.user import User
from app.security.auth import hash_password

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "admin@todo.com.br"
ADMIN_PASSWORD = "senha123"


def create_default_admin() -> None:
    db: Session = SessionLocal()
    try:
        existing = (
            db.query(User)
            .filter(User.email == ADMIN_EMAIL, User.deleted_at.is_(None))
            .first()
        )

        if existing:
            logger.info("Default admin already exists: %s", ADMIN_EMAIL)
            return

        admin_user = User(
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            name="Admin",
            role="admin",
        )

        db.add(admin_user)
        try:
            db.commit()
            logger.info("Default admin created: %s", ADMIN_EMAIL)
        except IntegrityError:
            db.rollback()
            logger.info(
                "Default admin creation skipped due to IntegrityError (probably exists)."
            )
    finally:
        db.close()
