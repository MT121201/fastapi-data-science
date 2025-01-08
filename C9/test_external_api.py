import asyncio
from typing import Any

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import status

from C9.app import app, external_api
from C9.test_app import test_client, event_loop


class MockExternalAPI:
    mock_data = {
        "products": [
            {
                "id": 1,
                "title": "iPhone 9",
                "description": "An apple mobile which is nothing like apple",
                "thumbnail": "https://i.dummyjson.com/data/products/1/thumbnail.jpg",
            },
        ],
        "total": 1,
        "skip": 0,
        "limit": 30,
    }

    async def __call__(self)->dict[str, Any]:
        return MockExternalAPI.mock_data


@pytest.mark.asyncio
async def test_external_products(test_client: httpx.AsyncClient):
    response = await test_client.get("/products")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == MockExternalAPI.mock_data