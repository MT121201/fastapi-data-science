import asyncio
import contextlib

from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel

broadcast = Broadcast("redis://localhost:6379")
CHANNEL_NAME = "chat"

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await broadcast.connect()
    yield
    await broadcast.disconnect()

app = FastAPI(lifespan=lifespan)


class MessageEvent(BaseModel):
    username: str
    message: str

async def receive_message(websocket: WebSocket, username: str):
    async with broadcast.subscribe(channel = CHANNEL_NAME) as subscriber:
        async for event in subscriber:
            message = MessageEvent.model_validate_json(event.message)
            if message.username != username:
                await websocket.send_json(message.model_dump())

async def send_message(websocket: WebSocket, username: str):
    data = await websocket.receive_text()
    event = MessageEvent(username=username, message=data)
    await broadcast.publish(channel = CHANNEL_NAME, message = event.model_dump_json())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: str = "anonymous"):
    await websocket.accept()
    try:
        while True:
            receive_task = asyncio.create_task(receive_message(websocket, username))
            send_message_task = asyncio.create_task(send_message(websocket, username))
            done, pending = await asyncio.wait(
                [receive_task, send_message_task], return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        pass