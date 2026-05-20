from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NameSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    is_published: bool = True

class NameResponseSchema(BaseModel):
    id: int
    name: str
    normalized_name: Optional[str]
    is_published: bool

    class Config:
        from_attributes = True


class ImageSchema(BaseModel):
    alt_text: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    order: int = 0


class ImageResponseSchema(BaseModel):
    id: int
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    original_name: Optional[str] = None
    alt_text: Optional[str] = None
    title: Optional[str] = None
    order: int

    class Config:
        from_attributes = True