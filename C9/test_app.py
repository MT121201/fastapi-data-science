import asyncio
import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import status
from C9.app import app

#automatically requested by pytest-asyncio before
# executing asynchronous tests
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_client():
    # ensures startup and shutdown events are executed
    async with LifespanManager(app):
        # ensures that an HTTP session is ready
        async with httpx.AsyncClient(app=app, base_url="http://app.io") as test_client:
            yield test_client


@pytest.mark.asyncio
# asynchronous test should be decorated with this marker
async def test_hello_world(test_client: httpx.AsyncClient):
    response = await test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Hello": "World"}


@pytest.mark.asyncio
class TestCreatePerson:
    async def test_invalid(self, test_client: httpx.AsyncClient):
        payload = {"name": "John", "lastname": "Doe"}
        response = await test_client.post("/person", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_valid(self, test_client: httpx.AsyncClient):
        payload = {"name": "John", "lastname": "Doe", "age": 30}
        response = await test_client.post("/person", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"name": "John", "lastname": "Doe", "age": 30}