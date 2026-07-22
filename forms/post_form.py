from fastapi import Form, File, UploadFile
from typing import Annotated

from schemas.post import PostCreate, PostUpdate


class PostCreateForm:
    def __init__(
        self,
        name: Annotated[str, Form(...)],
        text: Annotated[str, Form(...)],
        images: Annotated[list[UploadFile], File()] = []
    ):
        self.name = name
        self.text = text
        self.images = images

    async def validate(self) -> PostCreate:
        return PostCreate(
            name=self.name,
            text=self.text
        )


class PostUpdateForm:
    def __init__(
        self,
        name: Annotated[str, Form(...)],
        text: Annotated[str, Form(...)],
        new_images: Annotated[list[UploadFile], File()] = [],
        deleted_image_ids: Annotated[list[int], Form()] = [],
    ):
        self.name = name
        self.text = text
        self.new_images = new_images
        self.deleted_image_ids = deleted_image_ids

    async def validate(self) -> PostUpdate:
        return PostUpdate(
            name=self.name,
            text=self.text,
        )