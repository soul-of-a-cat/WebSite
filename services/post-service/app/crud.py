from sqlalchemy.orm import selectinload

from database import AsyncSession
from sqlalchemy import select, update, delete, func, or_, and_
from typing import Optional, List, Tuple, Dict, Any
import models, schemas
from datetime import datetime

class PostCRUD:
    @staticmethod
    async def create(db: AsyncSession, post: schemas.PostCreate, owner_id: int) -> models.Post:
        temp_post = models.Post(name=post.name)
        normalized_name = temp_post.normalized_name
        await models.Post.validate_unique_normalized_name(db, normalized_name)

        db_post = models.Post(
            name=post.name,
            text=post.text,
            is_published=True,
            user_id=owner_id,
            normalized_name=normalized_name,
        )
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post

    @staticmethod
    async def get_post(db: AsyncSession, post_id: int, include_images: bool = True) -> Optional[models.Post]:
        stmt = select(models.Post).where(models.Post.id == post_id)
        if include_images:
            stmt = stmt.options(selectinload(models.Post.images))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, post_update: schemas.PostUpdate, post_id: int) -> Optional[models.Post]:
        db_post = await PostCRUD.get_post(db, post_id, include_images=False)
        if not db_post:
            return None

        update_data = post_update.model_dump(exclude_unset=True)

        if "name" in update_data:
            temp_post = models.Post(name=update_data["name"])
            normalized_name = temp_post.normalized_name
            await models.Post.validate_unique_normalized_name(db, normalized_name, post_id)
            update_data["normalized_name"] = normalized_name

        for field, value in update_data.items():
            setattr(db_post, field, value)

        db_post.updated = datetime.utcnow()

        await db.commit()
        await db.refresh(db_post)
        return db_post

    @staticmethod
    async def delete(db: AsyncSession, post_id: int) -> bool:
        db_post = await PostCRUD.get_post(db, post_id, include_images=False)
        if not db_post:
            return False

        await db.delete(db_post)
        await db.commit()
        return True

    @staticmethod
    async def get_posts(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[schemas.PostFilter] = None,
            sort: Optional[schemas.PostSort] = None,
    ) -> List[models.Post]:
        stmt = select(models.Post).options(selectinload(models.Post.images))

        if filters:
            conditions = []

            if filters.search and filters.search.strip():
                search_pattern = f"%{filters.search.strip()}%"
                search_conditions = or_(
                    models.Post.name.ilike(search_pattern),
                    models.Post.text.ilike(search_pattern),
                )
                conditions.append(search_conditions)

            if filters.is_published is not None:
                conditions.append(models.Post.is_published == filters.is_published)

            if filters.user_id:
                conditions.append(models.Post.user_id == filters.user_id)

            if filters.date_from:
                date_to_start = filters.date_from.replace(hour=0, minute=0, second=0)
                conditions.append(models.Post.created >= date_to_start)

            if filters.date_to:
                date_to_end = filters.date_to.replace(hour=23, minute=59, second=59)
                conditions.append(models.Post.created <= date_to_end)

            if conditions:
                stmt = stmt.where(and_(*conditions))

        if sort:
            if hasattr(models.Post, sort.sort_by):
                sort_field = getattr(models.Post, sort.sort_by)
                if sort.sort_order == "desc":
                    sort_field = sort_field.desc()
                stmt = stmt.order_by(sort_field)
            else:
                stmt = stmt.order_by(models.Post.created.desc())
        else:
            stmt = stmt.order_by(models.Post.created.desc())

        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def post_count(db: AsyncSession, filters: Optional[schemas.PostFilter] = None) -> int:
        stmt = select(func.count(models.Post.id))

        if filters:
            conditions = []

            if filters.search and filters.search.strip():
                search_pattern = f"%{filters.search.strip()}%"
                search_conditions = or_(
                    models.Post.name.ilike(search_pattern),
                    models.Post.text.ilike(search_pattern),
                )
                conditions.append(search_conditions)

            if filters.is_published is not None:
                conditions.append(models.Post.is_published == filters.is_published)

            if filters.user_id:
                conditions.append(models.Post.user_id == filters.user_id)

            if filters.date_from:
                date_to_start = filters.date_from.replace(hour=0, minute=0, second=0)
                conditions.append(models.Post.created >= date_to_start)

            if filters.date_to:
                date_to_end = filters.date_to.replace(hour=23, minute=59, second=59)
                conditions.append(models.Post.created <= date_to_end)

            if conditions:
                stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        return result.scalar()

    @staticmethod
    async def bulk_create(db: AsyncSession, posts: List[schemas.PostCreate], owner_id: int) -> List[models.Post]:
        db_posts = []

        for post in posts:
            temp_post = models.Post(name=post.name)
            normalized_name = temp_post.normalized_name
            await models.Post.validate_unique_normalized_name(db, normalized_name)

            db_post = models.Post(
                name=post.name,
                text=post.text,
                is_published=True,
                user_id=owner_id,
                normalized_name=normalized_name
            )

            db_posts.append(db_post)

        db.add_all(db_posts)
        await db.commit()

        for post in db_posts:
            await db.refresh(post)

        return db_posts

    @staticmethod
    async def bulk_update(db: AsyncSession, post_ids: List[int], update_data: schemas.PostUpdate) -> Tuple[int, int]:
        if not post_ids:
            return 0, 0

        stmt = select(models.Post.id).where(models.Post.id.in_(post_ids))
        result = await db.execute(stmt)
        existing_ids = set(result.scalars().all())

        valid_ids = [post_id for post_id in post_ids if post_id in existing_ids]

        if not valid_ids:
            return 0, 0

        data_dict = update_data.model_dump(exclude_unset=True)

        if "name" in data_dict:
            temp_post = models.Post(name=data_dict["name"])
            data_dict["normalized_name"] = temp_post.normalized_name

        data_dict["updated"] = datetime.utcnow()
        
        update_stmt = (
            update(models.Post)
            .where(models.Post.id.in_(valid_ids))
            .values(**data_dict)
        )

        result = await db.execute(update_stmt)
        await db.commit()
        
        return len(valid_ids), result.rowcount

    @staticmethod
    async def bulk_delete(db: AsyncSession, post_ids: List[int]) -> int:
        if not post_ids:
            return 0

        delete_stmt = delete(models.Post).where(models.Post.id.in_(post_ids))
        result = await db.execute(delete_stmt)
        await db.commit()

        return result.rowcount

    @staticmethod
    async def get_post_stats(db: AsyncSession, user_id: Optional[int] = None) -> Dict[str, Any]:
        conditions = []
        if user_id is not None:
            conditions.append(models.Post.user_id == user_id)

        where_clause = and_(*conditions) if conditions else True

        total_stmt = select(func.count(models.Post.id)).select_from(where_clause)
        total_result = await db.execute(total_stmt)
        total_posts = total_result.scalar() or 0

        published_conditions = [models.Post.is_published == True]
        if user_id is not None:
            published_conditions.append(models.Post.user_id == user_id)
        published_stmt = select(func.count(models.Post.id)).where(and_(*published_conditions))
        published_result = await db.execute(published_stmt)
        published_posts = published_result.scalar() or 0

        posts_by_month_stmt = (
            select(
                func.extract("year", models.Post.created).label("year"),
                func.extract("month", models.Post.created).label("month"),
                func.count(models.Post.id).label("count"),
            )
            .group_by("year", "month")
            .order_by("year", "month")
        )

        if user_id:
            posts_by_month_stmt = posts_by_month_stmt.where(models.Post.user_id == user_id)

        posts_by_month_result = await db.execute(posts_by_month_stmt)
        posts_by_month = []
        for row in posts_by_month_result.all():
            year = int(row.year) if row.year else 0
            month = int(row.month) if row.month else 0
            count = int(row.count) if row.count else 0
            posts_by_month.append({
                "year": year,
                "month": month,
                "count": count
            })

        return {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "posts_by_month": posts_by_month,
        }

class PostImageCRUD:
    @staticmethod
    async def create(db: AsyncSession, post_id: int, image_file) -> Optional[models.PostImage]:
        post = await PostCRUD.get_post(db, post_id, include_images=False)
        if not post:
            return None

        db_image = models.PostImage(post_id=post_id)
        try:
            await db_image.save_image(image_file, db)
            await db.refresh(db_image)
            return db_image
        except Exception:
            await db.rollback()
            return None

    @staticmethod
    async def delete(db: AsyncSession, image_id: int) -> bool:
        stmt = select(models.PostImage).where(models.PostImage.id == image_id)
        result = await db.execute(stmt)
        db_image = result.scalar_one_or_none()

        if not db_image:
            return False

        await db.delete(db_image)
        await db.commit()
        return True

    @staticmethod
    async def get_by_post(db: AsyncSession, post_id: int) -> List[models.PostImage]:
        stmt = (
            select(models.PostImage)
            .where(models.PostImage.post_id == post_id)
            .order_by(models.PostImage.id)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())