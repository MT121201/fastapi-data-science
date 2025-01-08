import asyncio
import os

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from bson import ObjectId
from fastapi import status
from motor.motor_asyncio import AsyncIOMotorClient

from C6.demo_mongo.app import app, get_database
from C6.demo_mongo.models import Post

from C9.test_app import test_client, event_loop

motor_client = AsyncIOMotorClient(
    os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
)
database_test = motor_client["test_db"]

def get_test_db():
    return database_test

@pytest_asyncio.fixture(autouse=True, scope="module")
# autouse: call pytest to automatically call this fixture even if it’s not requested in any test
async def initialize_post():
    initial_posts = [
        Post(title="Post 1", content="Content 1"),
        Post(title="Post 2", content="Content 2"),
        Post(title="Post 3", content="Content 3"),
    ]
    await database_test["post"].insert_many(post.model_dump(by_alias=True) for post in initial_posts)
    yield initial_posts
    await motor_client.drop_database("test_db")

@pytest.mark.asyncio
class TestGetPost:
    async def test_not_exiting(self, test_client: httpx.AsyncClient):
        response = await test_client.get("/posts/60e17165334757001968785e")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_existing(self, test_client: httpx.AsyncClient, initialize_psot: list[Post]):
        response = await test_client.get(f"posts/{initialize_psot[0].id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == initialize_psot[0].model_dump(by_alias=True)

@pytest.mark.asyncio
class TestCreatePost:
    async def test_invalid(self, test_client: httpx.AsyncClient):
        payload = {"title": "Post 4"}
        response = await test_client.post("/posts", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_valid(self, test_client: httpx.AsyncClient):
        payload = {"title": "Post 4", "content": "Content 4"}
        response = await test_client.post("/posts", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        json = response.json()
        post_id = ObjectId(json["_id"])
        post_db = await get_database()["post"].find_one({"_id": post_id})
        assert post_db is not None