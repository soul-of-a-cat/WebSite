from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles

from core.config import settings
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="homepage/main.html",
        context={}
    )