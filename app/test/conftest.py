import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.database import database, usuarios_table

os.environ["ENV_STATE"] = "test"

from app.database import database
from app.main import app

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"

@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)

@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()

@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac

@pytest.fixture()
async def register_user(async_client: AsyncClient) -> None:
    user_details = {
        "email": "test@example.com","password": "password","nombre": "Test User","direccion": "Test Address","telefono": "1234567890","rol": "user","permiso": "user",
        }
    await async_client.post("/register/", json=user_details)
    query = usuarios_table.select().where(usuarios_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user["id"]
    return user_details

@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, register_user: dict) -> str:
    response = await async_client.post("/token/", json={"email": register_user["email"], "password": "password"})
    return response.json()["token"]