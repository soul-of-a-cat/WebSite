from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from core.config import settings
from api.routes.posts import router as posts_router
from api.routes.homepage import router as homepage_router
from core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(posts_router)
app.include_router(homepage_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
