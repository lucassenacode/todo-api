# app/main.py
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.core.init_admin import create_default_admin
from app.routers import admin_router, auth_router, task_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida da aplicação.
    Executa na inicialização e finalização.
    """
    # Startup
    if "pytest" not in sys.modules and os.getenv("TESTING") != "1":
        # Só cria o admin no ambiente "normal"
        create_default_admin()

    yield

    # Shutdown (se precisar no futuro, adiciona aqui)
    # ex: fechar conexões, limpar recursos, etc.


app = FastAPI(
    title="Todo API",
    description="API para gerenciamento de tarefas (Todo List)",
    version="0.1.0",
    lifespan=lifespan,
)

# Rotas
app.include_router(auth_router.router)
app.include_router(task_router.router)
app.include_router(user_router.router)
app.include_router(admin_router.router)


@app.get("/health", tags=["Health Check"], status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


@app.get("/ready", tags=["Health Check"], status_code=status.HTTP_200_OK)
def readiness_check():
    return {"database": "ok"}
