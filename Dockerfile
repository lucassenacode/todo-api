# Dockerfile
FROM python:3.13-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# deps de sistema: psycopg2 + build do bcrypt (caso precise)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    python3-dev \
    curl \
    git \
 && rm -rf /var/lib/apt/lists/*
# instala pip deps primeiro (aproveita cache)
COPY requirements.txt .
RUN pip install -r requirements.txt

# copia código e migrações
COPY ./app /app/app
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

# entrypoint
COPY scripts/entrypoint.sh /entrypoint.sh
# garante LF e permissão de execução (evita problema CRLF no Windows)
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
