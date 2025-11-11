import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.core.init_admin import create_default_admin
from app.routers import admin_router, auth_router, task_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if "pytest" not in sys.modules and os.getenv("TESTING") != "1":
        create_default_admin()
    yield


app = FastAPI(
    title="Todo API",
    description="API para gerenciamento de tarefas",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router.router)
app.include_router(task_router.router)
app.include_router(user_router.router)
app.include_router(admin_router.router)


@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


@app.get("/ready", tags=["Health"], status_code=status.HTTP_200_OK)
def readiness_check():
    # Se quiser, no futuro, você pode plugar um check real de DB aqui.
    return {"database": "ok"}
