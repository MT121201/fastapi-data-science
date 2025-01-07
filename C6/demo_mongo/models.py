from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObject(ObjectId):
    @classmethod
    def __getvalidators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MongoBaseModel(BaseModel):
    id: PyObject = Field(default_factory=PyObject, alias="_id")
    # Allows MongoDB's `_id` field to be mapped to `id` in the code.
    class Config:
        # allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class CommentBase(BaseModel):
    publication_date: datetime = Field(default_factory=datetime.now)
    content: str

class Comment(CommentBase):
    pass

class CommentCreate(CommentBase):
    pass

class PostBase(MongoBaseModel):
    title: str
    content: str
    publication_date: datetime = Field(default_factory=datetime.now)

class PostPartialUpdate(BaseModel):
    title: str | None = None
    content: str = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    comments: list[Comment] = Field(default_factory=list)
