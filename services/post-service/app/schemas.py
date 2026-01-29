from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, ConfigDict

class BaseResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ImageBase(BaseModel):
    image_path: Optional[str] = None
    thumbnail_path: Optional[str] = None

class ImageCreate(BaseModel):
    image: bytes
    filename: str

    @validator("filename")
    def validator_filename(cls, v):
        if '.' in v:
            ext = v.rsplit('.', 1)[1].lower()  # Берем последнюю часть после точки
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                raise ValueError('Неподдерживаемый формат файла')
        return v

class ImageResponse(ImageBase, BaseResponseSchema):
    id: int
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    post_id: int

    @validator('image_url', 'thumbnail_url', pre=True)
    def convert_urls(cls, v, info):
        if info.field_name == 'image_url' and hasattr(v, 'image_url'):
            return v.image_url
        elif info.field_name == 'thumbnail_url' and hasattr(v, 'thumbnail_url'):
            return v.thumbnail_url
        return v

class PostBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Название поста")
    text: str = Field(..., min_length=2, description="Текст поста")
    is_published: bool = Field(default=False, description="Опубликован ли пост")
    user_id: int = Field(..., description="ID пользователя")

class PostCreate(PostBase):
    @validator('name', 'text')
    def check_not_empty(cls, v, field):
        if not v.strip():
            raise ValueError(f'{field.name} не может быть пустым')
        return v

class PostUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150, description="Название поста")
    text: Optional[str] = Field(None, min_length=2, description="Текст поста")
    is_published: Optional[bool] = Field(None, strict=True, description="Опубликован ли пост")

    @validator('name', 'text')
    def check_if_not_empty(cls, v, field):
        if v is not None and not v.strip():
            raise ValueError(f'{field.name} не может быть пустым')
        return v

class PostResponse(PostBase, BaseResponseSchema):
    id: int
    normalized_name: str
    created: datetime
    updated: datetime
    images: List[ImageResponse] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class PostListResponse(BaseResponseSchema):
    id: int
    name: str
    normalized_name: str
    is_published: bool
    created: datetime
    updated: datetime
    preview_text: Optional[str] = None
    thumbnail_url: Optional[str] = None

    @validator("preview_text", pre=True)
    def extract_preview(cls, v, values):
        if "text" in values:
            text = values["text"]
            return text[:200] + "..." if len(text) > 200 else text
        return v

    @validator("thumbnail_url", pre=True)
    def get_first_thumbnail(cls, v, values):
        if 'images' in values and values['images']:
            return values['images'][0].thumbnail_url
        return None

class PostFilter(BaseModel):
    search: Optional[str] = Field(None, description="Поиск по названию или тексту")
    is_published: Optional[bool] = Field(None, description="Фильтр по статусу публикации")
    user_id: Optional[int] = Field(None, description="Фильтр по ID пользователя")
    date_from: Optional[datetime] = Field(None, description="Дата создания от")
    date_to: Optional[datetime] = Field(None, description="Дата создания до")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class PostSort(BaseModel):
    sort_by: str = Field(default="created", description="Поле для сортировки")
    sort_order: str = Field(default="desc", description="Порядок сортировки (asc/desc)")

    @validator("sort_by")
    def validate_sort_field(cls, v):
        allowed_fields = ["id", "name", "created", "updated", "user_id"]
        if v not in allowed_fields:
            raise ValueError(f"Допустимые поля для сортировки: {', '.join(allowed_fields)}")
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v.lower() not in ['asc', 'desc']:  # Приводим к нижнему регистру
            raise ValueError('Порядок сортировки должен быть "asc" или "desc"')
        return v.lower()

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Номер страницы")
    per_page: int = Field(default=20, ge=1, le=100, description="Количество элементов на странице")

class PaginationResponse(BaseModel):
    items: List[PostListResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class PostDetailResponse(PostResponse):
    image_count: int

    @validator("image_count", pre=True)
    def count_images(cls, v, values):
        if "images" in values:
            return len(values["images"])
        return 0

class BulkPostCreate(BaseModel):
    posts: List[PostCreate] = Field(..., max_items=100, description="Список постов")

    @validator("posts")
    def validate_unique_names(cls, v):
        names = [post.name for post in v]
        if len(names) != len(set(names)):
            raise ValueError('Имена постов должны быть уникальными')
        return v

class BulkPostUpdate(BaseModel):
    post_ids: List[int] = Field(..., max_items=100, description="ID постов для обновления")
    data: PostUpdate

class PostStatsResponse(BaseModel):
    total_posts: int
    published_posts: int
    draft_posts: int
    posts_by_month: List[dict]
    average_images_per_post: float
    most_active_user: Optional[int] = None
