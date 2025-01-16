from datetime import datetime
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str
    content: str
    publication_date: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True


class PostPartialUpdate(BaseModel):
    title: str | None = None
    content: str = None

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    comments: list[dict]

class CommentBase(BaseModel):
    publication_date: datetime = Field(default_factory=datetime.now)
    content: str

    class Config:
        orm_mode = True

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int

