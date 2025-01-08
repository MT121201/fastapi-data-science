import asyncio

import pytest
import pytest_asyncio
import httpx
from asgi_lifespan import LifespanManager
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from C9.ws import app
from C9.test_app import event_loop

@pytest_asyncio.fixture
async def test_client():
    async with LifespanManager(app):
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app),
            base_url="ws://app.io",
        ) as test_client:
            yield test_client

@pytest.mark.asyncio
async def test_ws_echo(test_client: httpx.AsyncClient):
    async with aconnect_ws("/ws", test_client) as ws:
        await ws.send_text("Hello")
        response = await ws.receive_text()
        assert response == "Message text was: Hello"