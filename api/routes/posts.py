from typing import Annotated

from fastapi import Request, APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, HTMLResponse

from core.database import get_async_session
from core.templates import templates
from models.user import User
from services.post_service import PostService
from forms.post_form import PostCreateForm, PostUpdateForm

from api.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/create", response_class=HTMLResponse, name="create_post")
async def create_post_page(
        request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="posts/post_create.html",
        context={}
    )

@router.post("/create", name="create_post")
async def create_post(
        form: Annotated[PostCreateForm, Depends()],
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    data = await form.validate()
    await PostService.create(
        session=session,
        data=data,
        images=form.images,
        user=current_user
    )
    return RedirectResponse(
        url="/",
        status_code=303
    )

@router.get("/{post_id}", name="post_detail")
async def post_detail(
        request: Request,
        post_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    post = await PostService.get_by_id(session, post_id)
    return templates.TemplateResponse(
        request=request,
        name="posts/post.html",
        context={
            "post": post
        }
    )

@router.get("delete/{post_id}", name="delete_post")
async def delete_post(
        request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="posts/post_delete.html",
        context={}
    )

@router.post("/delete/{post_id}", name="delete_post")
async def delete_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    post = await PostService.get_by_id(session, post_id)
    await PostService.delete(
        session=session,
        post=post,
        user=current_user
    )
    return RedirectResponse("/")

@router.post("/update/{post_id}", name="update_post")
async def update_post(
        post_id: int,
        form: Annotated[PostUpdateForm, Depends()],
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    data = await form.validate()
    await PostService.update(
        session=session,
        post_id=post_id,
        data=data,
        deleted_images_ids=form.deleted_image_ids,
        new_images=form.new_images,
        user=current_user
    )

    return RedirectResponse(
        url="/",
        status_code=303
    )