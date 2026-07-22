from fastapi import Request, APIRouter
from core.templates import templates

router = APIRouter()

@router.get("/", name="home")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="homepage/main.html",
        context={
            "posts": []
        }
    )