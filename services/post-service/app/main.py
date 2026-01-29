from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from database import get_async_session, AsyncSession

from schemas import (
    PostCreate, PostUpdate, PostResponse,
    PostFilter, PostSort, PaginationParams,
    PaginationResponse, ImageResponse, PostDetailResponse
)

from models import Post, PostImage

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse)
async def create_post(
        post_data: PostCreate,
        db: AsyncSession = Depends(get_async_session),
):
    temp_post = Post(name=post_data.name)
    normalized_name = temp_post.normalized_name
    await Post.validate_unique_normalized_name(db, normalized_name)

    post = Post(
        name=post_data.name,
        text=post_data.text,
        is_published=True,
        user_id=post_data.user_id,
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post

@router.get("/", response_model=PaginationResponse)
async def get_posts(
        filter_params: PostFilter = Depends(),
        sort_params: PostSort = Depends(),
        pagination: PaginationParams = Depends(),
        db: AsyncSession = Depends(get_async_session),
):
    query = select(Post).options(selectinload(Post.images))

    if filter_params.search:
        query = query.where(
            (Post.name.ilike(f"%{filter_params.search}%")) |
            (Post.text.ilike(f"%{filter_params.search}%"))
        )

    if filter_params.is_published is not None:
        query = query.where(Post.is_published == filter_params.is_published)

    if filter_params.user_id is not None:
        query = query.where(Post.user_id == filter_params.user_id)

    if filter_params.date_from:
        query = query.where(Post.created >= filter_params.date_from)

    if filter_params.date_to:
        query = query.where(Post.created <= filter_params.date_to)

    order_column = getattr(Post, sort_params.sort_by)
    if sort_params.sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (pagination.page - 1) * pagination.per_page
    query = query.offset(offset).limit(pagination.per_page)

    result = await db.execute(query)
    posts = result.scalars().all()

    return PaginationResponse(
        items=posts,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=(total + pagination.per_page - 1) // pagination.per_page
    )


@router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post(
        post_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    query = select(Post).options(selectinload(Post.images)).where(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
        post_id: int,
        update_data: PostUpdate,
        db: AsyncSession = Depends(get_async_session)
):
    query = select(Post).where(Post.id == post_id)
    result = await db.execute(query)
    post    = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    update_dict = update_data.dict(exclude_unset=True)

    if 'name' in update_dict:
        temp_post = Post(name=update_dict['name'])
        new_normalized = temp_post.normalized_name
        await Post.validate_unique_normalized_name(db, new_normalized, post_id)
        update_dict['normalized_name'] = new_normalized

    for field, value in update_dict.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)

    return post


@router.delete("/{post_id}")
async def delete_post(
        post_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    query = select(Post).where(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    await db.delete(post)
    await db.commit()

    return {"message": "Пост успешно удален"}


@router.post("/{post_id}/images/", response_model=ImageResponse)
async def upload_post_image(
        post_id: int,
        image_file: UploadFile,
        db: AsyncSession = Depends(get_async_session)
):
    post_query = select(Post).where(Post.id == post_id)
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    post_image = PostImage(post_id=post_id)

    await post_image.save_image(image_file, db)

    return post_image


@router.get("/{post_id}/images/", response_model=List[ImageResponse])
async def get_post_images(
        post_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    query = select(PostImage).where(PostImage.post_id == post_id)
    result = await db.execute(query)
    images = result.scalars().all()

    return images