import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["TESTING"] = "true"

from app.core.config import settings  # noqa: E402
from app.db.database import Base, get_db_session  # noqa: E402
from app.main import app  # noqa: E402

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
        db.rollback()
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.pop(get_db_session, None)
