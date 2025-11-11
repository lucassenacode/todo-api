# Todo API (Projeto de Portfólio)

![API CI Pipeline](https://github.com/lucassenacode/todo-api/actions/workflows/ci.yml/badge.svg)

Uma API RESTful completa para um sistema **To-Do List** multiusuário, construída com **Python 3.13** e **FastAPI**.

O objetivo deste projeto é demonstrar práticas profissionais de backend:

- **Arquitetura limpa:** Separação clara entre **Routers**, **Services**, **Repositories** e **Models**.
- **Banco de dados versionado:** Migrações com **Alembic**.
- **CI/CD completo:** GitHub Actions executando **Ruff (lint/format)**, **Trivy (segurança)** e **Pytest** a cada commit.
- **Testes automatizados:** Cobertura de unidade e integração (auth, tasks, perfil, admin).
- **Infraestrutura como Código (IaC):** Deploy automatizado definido em `render.yaml` (Render).

---

## 🚀 Stack de Tecnologia

- **Linguagem:** Python 3.13
- **Framework Web:** FastAPI
- **Banco de Dados:** PostgreSQL
  - Local via Docker
  - Produção via **Neon** (Postgres serverless)
- **Containerização:** Docker & Docker Compose
- **Migrações:** Alembic
- **Testes:** Pytest + FastAPI TestClient
- **Segurança:**
  - JWT (`python-jose`)
  - Hash de senha com `passlib[bcrypt]`
- **Qualidade de Código:** Ruff
- **CI/CD:** GitHub Actions
- **Deploy:** Render (`render.yaml`)

---

## ✨ Funcionalidades

### 🔐 Autenticação (`/api/auth`)

- `POST /api/auth/register`
  - Registo de novos usuários.
  - Senha armazenada com hash `bcrypt`.
- `POST /api/auth/login`
  - Autenticação usando `OAuth2PasswordRequestForm`.
  - Retorna:
    - `access_token` (JWT)
    - `refresh_token` (JWT)
    - `token_type = "bearer"`.

### ✅ Gestão de Tarefas (`/api/tasks`)

- CRUD completo:
  - `POST /api/tasks/`
  - `GET /api/tasks/`
  - `GET /api/tasks/{id}`
  - `PUT /api/tasks/{id}`
  - `DELETE /api/tasks/{id}` (soft delete)
- **Ownership:** Usuário só acessa as **próprias tarefas**.
- **Soft Delete:** Campo `deleted_at` em vez de remoção física.
- **Regras de negócio:**
  - Novas tarefas começam como `pending`.
  - Suporte a filtro por status e paginação.

### 👤 Gestão de Perfil (`/api/users`)

- `GET /api/users/me`
  - Retorna dados do usuário autenticado.
- `PUT /api/users/me`
  - Atualiza `name` e/ou `new_password`.
  - Não permite alterar `email`.
- `DELETE /api/users/me`
  - Soft delete da própria conta.

### 🛠️ Admin (`/api/admin`)

- `GET /api/admin/dashboard`
  - **Protegido por role `admin`.**
  - Retorna métricas:
    - `total_users`
    - `total_tasks`
    - `total_tasks_pending`
    - `total_tasks_completed`
- Um usuário admin padrão pode ser criado automaticamente na inicialização (apenas fora de ambiente de teste).

---

## 🏃 Como Rodar Localmente

**Requisitos:**

- Docker
- Docker Compose

### 1. Clonar o repositório

```bash
git clone https://github.com/lucassenacode/todo-api.git
cd todo-api
