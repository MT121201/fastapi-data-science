import contextlib
from typing import Any

import httpx
from fastapi import FastAPI, status, Depends
from pydantic import BaseModel


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting app")
    yield
    print("Stopping app")


class ExternalAPI:
    def __init__(self)->None:
        self.client = httpx.AsyncClient(base_url="https://dummyjson.com")

    async def __call__(self)->dict[str, Any]:
        async with self.client as client:
            response = await client.get("/products")
            return response.json()



app=FastAPI(lifespan=lifespan)
external_api = ExternalAPI()


class Person(BaseModel):
    first_name: str
    last_name: str
    age: int




@app.post("/persons", status_code=status.HTTP_201_CREATED)
async def create_person(person: Person):
    return person

@app.get("/")
async def hello_world():
    return {"Hello": "World"}


@app.get("/products")
async def external_products(products: dict[str, Any] = Depends(external_api)):
    return products