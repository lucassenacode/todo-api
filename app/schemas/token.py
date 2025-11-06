# app/schemas/token.py
from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema para a resposta do endpoint /login.
    Conforme a Especificação de Produto.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
