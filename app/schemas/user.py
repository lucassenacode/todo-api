# app/schemas/user.py
from pydantic import BaseModel, EmailStr

# --- Schemas Base ---
# Usamos um Schema Base para campos comuns (como email)
# para evitar repetição e para validação.


class UserBase(BaseModel):
    """Schema base para o Utilizador, contém campos comuns."""

    email: EmailStr  # Valida que o email está num formato correto


# --- Schemas de API ---


class UserCreate(UserBase):
    """
    Schema para a criação de um novo utilizador (input para /register).
    Recebe o email (do Base) e a password.
    """

    password: str


class UserRead(UserBase):
    """
    Schema para a leitura de um utilizador (output do /register).
    Devolve o email (do Base) e o id.
    (NUNCA devolve a password).
    """

    id: int

    # Configuração Pydantic para permitir o mapeamento
    # de atributos de um modelo SQLAlchemy (ex: user.id)
    class Config:
        from_attributes = True
