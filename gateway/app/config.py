from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator, Field, HttpUrl
import secrets

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "WebSite"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)

    # Security
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_COOKIE_NAME : str = Field(default="access_token")
    ACCESS_TOKEN_COOKIE_SECURE: bool = Field(default=True)
    ACCESS_TOKEN_COOKIE_HTTPONLY: bool = Field(default=True)
    ACCES_TOKEN_COOKIE_SAMESITE: str = Field(default="Lax")
    CSRF_COOKIE_NAME: str = Field(default="csrf_token")
    CSRF_COOKIE_SECURE: bool = Field(default=True)
    CSRF_HEADER_NAME: str = Field(default="X-CSRF-Token")
    CSRF_TOKEN_LENGTH: int = Field(default=32)

    # Settings other services
    AUTH_SERVICE_URL: HttpUrl = Field(default="https://auth-service:8001")
    USER_SERVICE_URL: HttpUrl  = Field(default="https://user-service:8002")
    POST_SERVICE_URL: HttpUrl  = Field(default="https://post-service:8003")
    COMMENT_SERVICE_URL: HttpUrl  = Field(default="https://comment-service:8004")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default=["http://localhost:8000", "http://localhost:8000"],
    )

    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Разрешить credentials в CORS"
    )

    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Разрешенные HTTPS методы"
    )

    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        description="Разрешенные HTTPS заголовки"
    )

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Включить rate limiting")
    RATE_LIMIT_DEFAULT: str = Field(default="60/minute", description="Лимит по умолчанию")
    RATE_LIMIT_AUTH: str = Field(default="10/minute", description="Лимит для аутентификации")
    RATE_LIMIT_API: str = Field(default="1000/minute", description="Лимит для API")

    # IP блокировка
    IP_BLOCKLIST_ENABLED: bool = Field(default=True, description="Включить блокировку IP")
    IP_BLOCKLIST: List[str] = Field(default=[], description="Заблокированные IP адреса")

    # Защита от атак
    MAX_REQUEST_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Максимальный размер запроса"
    )

    REQUEST_TIMEOUT: int = Field(
        default=30,
        ge=1,
        description="Таймаут запроса в секундах"
    )

    @validator("AUTH_SERVICE_URL", "USER_SERVICE_URL", "POST_SERVICE_URL", "COMMENT_SERVICE_URL")
    def validate_service_urls(cls, v):
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("URL сервиса должен начинаться с http:// или https://")
        return v

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
