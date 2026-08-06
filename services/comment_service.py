from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comment import CommentModel, CommentImageModel
from models.post import PostModel
from models.user import User
from schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    @staticmethod
    async def create(
            session: AsyncSession,
            data: CommentCreate,
            images: list[UploadFile],
            user: User,
            post: PostModel
    ):
        comment = CommentModel(
            text=data.text,
            is_public=True,
            user=user
        )

        session.add(comment)
        await session.flush()

        for image in images:
            if not image.filename:
                continue

            comment_image = CommentImageModel(
                comment=comment,
            )

            await comment_image.save_upload(image)
            session.add(comment_image)

        await session.commit()
        await session.refresh(comment)

        return comment

    @staticmethod
    async def delete(
            session: AsyncSession,
            user: User,
            comment: CommentModel
    ):
        if comment.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав"
            )
        await session.delete(comment)
        await session.commit()

    @staticmethod
    async def update(
            session: AsyncSession,
            comment_id: int,
            data: CommentUpdate,
            deleted_images_ids: list[int],
            new_images: list[UploadFile],
            user: User
    ):
        result = await session.execute(
            select(PostModel)
            .options(selectinload(PostModel.images))
            .where(CommentModel.id == comment_id)
        )

        comment = result.scalar_one_or_none()

        if comment is None:
            raise HTTPException(404, "Пост не найден")

        if comment.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав"
            )

        comment.text = data.text

        for image_id in deleted_images_ids:
            image = await session.get(CommentImageModel, image_id)

            if image and image.comment_id == comment.id:
                await image.delete_image()
                await session.delete(image)

        await session.flush()

        for upload in new_images:
            if not upload.filename:
                continue

            new_image = CommentImageModel(
                comment=comment,
            )

            await new_image.save_upload(upload)
            session.add(new_image)

        await session.commit()
        await session.refresh(comment)

        return comment
