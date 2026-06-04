from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ============ Приложение ============
    APP_NAME: str = Field("My FastAPI App", env="APP_NAME")
    APP_VERSION: str = Field("1.0.0", env="APP_VERSION")
    APP_DESCRIPTION: str = Field("API для управления постами", env="APP_DESCRIPTION")
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")

    # ============ Сервер ============
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    WORKERS: int = Field(1, env="WORKERS")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_METHODS: List[str] = Field(["*"], env="ALLOWED_METHODS")
    ALLOWED_HEADERS: List[str] = Field(["*"], env="ALLOWED_HEADERS")

    # ============ База данных ============
    # SQLite
    SQLITE_DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///./app.db",
        env="SQLITE_DATABASE_URL"
    )

    # PostgreSQL
    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("postgres", env="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field("app", env="POSTGRES_DB")

    @property
    def DATABASE_URL(self) -> str:
        if self.ENVIRONMENT == "production":
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self.SQLITE_DATABASE_URL

    # Настройки пула соединений
    DB_POOL_SIZE: int = Field(20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(10, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(30, env="DB_POOL_TIMEOUT")
    DB_ECHO: bool = Field(False, env="DB_ECHO")

    # ============ Redis ============
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ============ JWT Аутентификация ============
    JWT_SECRET_KEY: str = Field("your-secret-key-change-in-production", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # ============ Файлы и медиа ============
    MEDIA_ROOT: str = Field("media", env="MEDIA_ROOT")
    MEDIA_URL: str = Field("/media/", env="MEDIA_URL")
    UPLOAD_DIR: str = Field("uploads", env="UPLOAD_DIR")

    # Настройки загрузки изображений
    MAX_UPLOAD_SIZE: int = Field(10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        env="ALLOWED_IMAGE_EXTENSIONS"
    )
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        ["image/jpeg", "image/png", "image/gif", "image/webp"],
        env="ALLOWED_IMAGE_TYPES"
    )

    # Размеры миниатюр
    THUMBNAIL_SIZES: dict = Field(
        {
            "small": (150, 150),
            "medium": (300, 300),
            "large": (800, 600)
        },
        env="THUMBNAIL_SIZES"
    )

    MAX_ATTEMPTS: int = Field(5, env="MAX_ATTEMPTS")

    # ============ Кеширование ============
    CACHE_ENABLED: bool = Field(True, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(300, env="CACHE_TTL")  # 5 минут
    CACHE_POSTS_TTL: int = Field(600, env="CACHE_POSTS_TTL")  # 10 минут

    # ============ Пагинация ============
    DEFAULT_PAGE_SIZE: int = Field(10, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(100, env="MAX_PAGE_SIZE")

    # ============ Логирование ============
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_FILE: Optional[str] = Field("logs/app.log", env="LOG_FILE")

    # ============ Email (опционально) ============
    SMTP_HOST: str = Field("smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(None, env="SMTP_PASSWORD")
    SMTP_FROM: str = Field("noreply@example.com", env="SMTP_FROM")
    SMTP_TLS: bool = Field(True, env="SMTP_TLS")

    # ============ Безопасность ============
    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(60, env="RATE_LIMIT_PERIOD")

    # Хеширование паролей
    PASSWORD_HASH_ALGORITHM: str = Field("bcrypt", env="PASSWORD_HASH_ALGORITHM")
    PASSWORD_MIN_LENGTH: int = Field(8, env="PASSWORD_MIN_LENGTH")

    # ============ Внешние сервисы ============
    S3_ENABLED: bool = Field(False, env="S3_ENABLED")
    S3_ENDPOINT: Optional[str] = Field(None, env="S3_ENDPOINT")
    S3_ACCESS_KEY: Optional[str] = Field(None, env="S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = Field(None, env="S3_SECRET_KEY")
    S3_BUCKET_NAME: str = Field("my-bucket", env="S3_BUCKET_NAME")
    S3_REGION: str = Field("us-east-1", env="S3_REGION")

    # Sentry для отслеживания ошибок
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")

    # ============ Тестирование ============
    TEST_DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///./test.db",
        env="TEST_DATABASE_URL"
    )

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    @field_validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value


# Создаем глобальный экземпляр настроек
settings = Settings()