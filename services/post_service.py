from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from schemas.post import PostCreate, PostUpdate
from models.post import PostModel, PostImageModel
from sqlalchemy import select

class PostService:
    @staticmethod
    async def create(
            session: AsyncSession,
            data: PostCreate,
            images: list[UploadFile]
    ) -> PostModel:
        post = PostModel(
            name=data.name,
            text=data.text,
            is_published=True,
            user_id=1,

        )
        post.set_normalized_name()

        session.add(post)
        await session.flush()

        for image in images:
            if not image.filename:
                continue

            post_image = PostImageModel(
                post=post
            )

            await post_image.save_upload(image)
            session.add(post_image)

        await session.commit()
        await session.refresh(post)

        return post

    @staticmethod
    async def get_by_id(
            session: AsyncSession,
            post_id: int
    ) -> PostModel | None:
        results = await session.execute(
            select(PostModel)
            .where(PostModel.id == post_id)
        )

        return results.scalar_one_or_none()

    @staticmethod
    async def delete(
            session: AsyncSession,
            post: PostModel
    ):
        await session.delete(post)
        await session.commit()

    @staticmethod
    async def update(
            session: AsyncSession,
            post_id: int,
            data: PostUpdate,
            deleted_images_ids: list[int],
            new_images: list[UploadFile],
    ) -> PostModel | None:
        result = await session.execute(
            select(PostModel)
            .options(selectinload(PostModel.images))
            .where(PostModel.id == post_id)
        )

        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(404, "Пост не найден")

        post.name = data.name
        post.text = data.text
        post.set_normalized_name()

        for image_id in deleted_images_ids:
            image = await session.get(PostImageModel, image_id)

            if image and image.post_id == post.id:
                await image.delete_image()
                await session.delete(image)

        await session.flush()

        for upload in new_images:
            if not upload.filename:
                continue

            new_image = PostImageModel(
                post=post
            )

            await new_image.save_upload(upload)
            session.add(new_image)

        await session.commit()
        await session.refresh(post)

        return post
