# tests/conftest.py (CORRIGIDO)
import os

# Define que estamos em modo de teste ANTES de importar qualquer

os.environ["TESTING"] = "true"

# 2. O resto das importações
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# 3. Agora estas importações vão usar o 'settings.DATABASE_URL' correto
from app.core.config import settings  # noqa: E402
from app.db.database import Base, get_db_session
from app.main import app

# Cria um motor de DB *apenas* para os testes
engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- 2. FIXTURES (O que os testes vão usar) ---


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Fixture de sessão: Cria a DB de teste uma vez e destrói-a no final.
    'autouse=True' garante que isto corre sempre.
    """
    try:
        # Tenta apagar tabelas antigas (se existirem de um teste falhado)
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass  # Ignora se as tabelas não existirem

    # Cria todas as tabelas (users, tasks)
    Base.metadata.create_all(bind=engine)

    yield  # Os testes correm aqui

    # Destrói todas as tabelas no final
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture de função: Cria uma sessão de DB limpa para CADA teste.
    Esta fixture é responsável por abrir e fechar a sessão.
    """
    db = TestingSessionLocal()
    try:
        yield db
        # uma boa prática para testes 'function-scoped'.
        db.rollback()
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture de função: Cria um cliente de API (TestClient) para CADA teste.
    Este cliente usa a sessão de DB de teste (db_session).
    """

    def override_get_db_session():
        """
        Substitui a dependência get_db_session pela sessão de teste.
        """
        yield db_session

    # Aplica a "substituição" (override)
    app.dependency_overrides[get_db_session] = override_get_db_session

    # Entrega o cliente ao teste
    with TestClient(app) as c:
        yield c

    # Limpa a "substituição" depois do teste
    app.dependency_overrides.pop(get_db_session, None)
