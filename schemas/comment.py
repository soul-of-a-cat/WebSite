from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from schemas.base import NameResponseSchema, NameSchema, ImageResponseSchema

class CommentCreate(NameSchema):
    text: str = Field(..., min_length=1, max_length=5000)

class CommentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    text: Optional[str] = Field(None, min_length=1, max_length=5000)
    is_published: Optional[bool] = None

class CommentImageUpdate(BaseModel):
    alt_text: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    order: Optional[int] = None

class CommentImageResponse(ImageResponseSchema):
    comment_id: int

class CommentResponse(NameResponseSchema):
    text: str
    created: datetime
    updated: datetime
    images: List[CommentImageResponse] = Field(default_factory=list)
    main_image_url: Optional[str] = None
    images_count: int = 0

class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    size: int
    pages: int