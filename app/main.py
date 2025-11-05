# app/main.py
from fastapi import FastAPI, status

# Criamos a aplicação FastAPI
app = FastAPI(
    title="Todo API",
    description="API para gerenciamento de tarefas (Todo List)",
    version="0.1.0",  # Começamos com 0.1.0, alinhado ao M0
)


@app.get("/health", tags=["Health Check"], status_code=status.HTTP_200_OK)
def health_check():
    """
    Verifica se a aplicação está "viva" (Liveness probe).
    """
    return {"status": "ok"}


@app.get("/ready", tags=["Health Check"], status_code=status.HTTP_200_OK)
def readiness_check():
    """
    Verifica se a aplicação está pronta para receber tráfego (Readiness probe).
    Por enquanto, é igual ao /health. No M4, verificará o banco.
    """
    # No M0, apenas retornar 'ok' é suficiente.
    # No M4, isso testaria a conexão com o banco.
    return {"database": "ok"}
