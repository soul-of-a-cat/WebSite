from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config import settings

# Асинхронный движок PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL-запросы в консоль (только для разработки)
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=20,  # Размер пула соединений
    max_overflow=40,  # Максимальное количество соединений сверх pool_size
    pool_recycle=3600,  # Пересоздавать соединения через час
    pool_timeout=30,  # Таймаут ожидания соединения
)

# Асинхронная фабрика сессий
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependency для получения асинхронной сессии БД
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
