from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, Field
import secrets

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # База данных
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="password")
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_DB: str = "post_db"
    DATABASE_URL: str = PostgresDsn().build(
        sheme="postgresql+psycopg2",
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_SERVER,
        port=POSTGRES_PORT,
        path=POSTGRES_DB,
    )
    DATABASE_POOL_SIZE: int = Field(default=20, ge=1, le=100)
    DATABASE_MAX_OVERFLOW: int = Field(default=0, ge=0)
    DATABASE_ECHO: bool = Field(default=False)

    # JWT
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)
    TOKEN_ISSUER: str = Field(default="auth-service")

    # Настройки приложения
    APP_NAME: str = "Post Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Path to SSL
    SSL_CERT_PATH: Optional[Path] = None
    SSL_KEY_PATH: Optional[Path] = None

    # Security settings
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    ALLOWED_PORT: str = "8003"
    API_KEY_HEADER: str = "X-API-KEY"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
