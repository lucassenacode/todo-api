# app/routers/auth_router.py
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.token import Token
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


@router.post(
    "/login",
    response_model=Token,  # O schema de resposta é o Token
)
def login_for_access_token(
    # A especificação pede OAuth2PasswordRequestForm.
    # O FastAPI injeta o 'form data' (username e password) nisto.
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
):
    """
    Endpoint para autenticar um utilizador e obter tokens JWT.
    Recebe 'username' (que é o email) e 'password' via form data.
    Retorna um access_token e refresh_token.
    """
    # 1. Instancia o Serviço
    user_service = UserService(db)
    # 2. Chama o método de login
    # (O serviço contém toda a lógica: encontrar, verificar, gerar token)
    # A especificação diz que 'username' é o email.
    token_data = user_service.login_user(
        email=form_data.username, password=form_data.password
    )
    # 3. Retorna o schema Token
    return token_data
