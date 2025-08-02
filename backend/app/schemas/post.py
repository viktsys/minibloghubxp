from pydantic import BaseModel, HttpUrl
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .comment import Comment


class PostBase(BaseModel):
    title: str
    content: str
    image_url: Optional[HttpUrl] = None
    image_caption: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    image_caption: Optional[str] = None


class PostInDB(PostBase):
    id: int
    author_id: int
    is_imported: bool
    external_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class Post(PostInDB):
    author: "User"
    comments: List["Comment"] = []


class PostImport(BaseModel):
    title: str
    content: str
    user_id: int
    external_id: int
