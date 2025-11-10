# app/core/config.py
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int = 5432
    TEST_DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    @property
    def DATABASE_URL(self) -> str:
        """
        Gera a URL de conexão do banco de dados.

        Se a variável de ambiente 'TESTING' estiver definida,
        usa a TEST_DATABASE_URL. Caso contrário, usa a DB normal.
        """
        if os.getenv("TESTING") == "true":
            return self.TEST_DATABASE_URL  # <-- Retorna a URL de teste

        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
