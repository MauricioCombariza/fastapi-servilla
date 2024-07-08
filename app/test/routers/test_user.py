from typing import Callable
import pytest
from httpx import AsyncClient

async def register_user(async_client: AsyncClient, email: str, password:str) -> None:
    return await async_client.post("/register/", json={"email": email, "password": password, "nombre": "Test User", "direccion": "Test Address", "telefono": "1234567890", "rol": "user", "permiso": "user"})

@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.com", "1234")
    assert response.status_code == 201
    assert "User created" in response.json()["detail"]

@pytest.mark.anyio
async def test_register_user_already_exists(async_client: AsyncClient, register_user: Callable):
    user_data = register_user()  # Llama a la función para obtener el diccionario
    response = await register_user(async_client, user_data['email'], user_data['password'])
    assert response.status_code == 400
    assert "User already exists" in response.json()["detail"]

@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post("/token/", json={"email": "test@example.com", "password": "1234"})
    assert response.status_code == 401

@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, register_user: dict):
    response = await async_client.post(
        "/token/",
        json={
            "email": register_user["email"],
            "password": register_user["password"]
            }
        )
    assert response.status_code == 200