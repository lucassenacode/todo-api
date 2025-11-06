# app/routers/auth_router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

# Cria um novo "router" (um mini-app FastAPI)
# Definimos o prefixo e as tags que serão aplicadas
# a todos os endpoints deste router.
router = APIRouter(
    prefix="/api/auth",  # Prefixo da URL (conforme Especificação)
    tags=["Authentication"],  # Tag para a documentação /docs
)


# --- Dependência de Sessão de DB ---
# Esta é a nossa função de "Injeção de Dependência".
# Ela garante que abrimos uma sessão de DB para cada request
# e que a fechamos (com 'finally') no final, mesmo se um erro ocorrer.
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoint de Registo ---


@router.post(
    "/register",
    response_model=UserRead,  # O schema de resposta (o que devolvemos)
    status_code=status.HTTP_201_CREATED,  # Código HTTP para sucesso (201 Created)
)
def register_user(
    user_create: UserCreate,  # O schema de input (o que recebemos)
    db: Session = Depends(get_db_session),  # Injeta a sessão de DB
):
    """
    Endpoint para registar um novo utilizador.

    - Recebe um email e password (schema UserCreate).
    - Aplica as regras de negócio (RN-01, RN-02) através do Service.
    - Retorna os dados do utilizador criado (schema UserRead).
    - Retorna 409 Conflict se o email já existir.
    """

    # 1. Instancia o Serviço (passando a sessão de DB)
    user_service = UserService(db)

    # 2. Chama o método do serviço
    # (O serviço contém toda a lógica: hash, verificação, criação)
    new_user = user_service.register_user(user_create)

    # 3. Retorna o utilizador (o FastAPI converte para UserRead)
    return new_user
