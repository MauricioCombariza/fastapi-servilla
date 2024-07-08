import pytest
from httpx import AsyncClient,  ASGITransport
from app.models.order import Order
from app.main import app
from starlette.testclient import TestClient

async def create_order(body: str,async_client: AsyncClient, logged_in_token: str) -> dict:
    response = await async_client.post("/order/", json={"body": body}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()

# crear una funcion para crear comentarios
async def create_comment(body: str, serial: int, async_client: AsyncClient, logged_in_token: str) -> dict:
    response = await async_client.post("/comments/", json={"body": body, "serial": serial}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()

# crear un fixture para crear comentarios
@pytest.fixture()
async def created_comment(async_client: AsyncClient, logged_in_token) -> dict:
    return await create_comment("Test_comment", 123, async_client, logged_in_token)


@pytest.fixture()
async def created_order(async_client: AsyncClient, logged_in_token:str) -> dict:
    return await create_order("Test_order", async_client, logged_in_token)

@pytest.mark.asyncio
async def test_create_order(async_client: AsyncClient, logged_in_token: str):
    body = "Test_order"
    response = await async_client.post("/order/", json={"body": body}, headers={"Authorization": f"Bearer {logged_in_token}"})
    assert response.status_code == 201
    assert {"id": 1, "body": body}.items() <= response.json().items()

@pytest.mark.asyncio
async def test_created_order_expired_token(async_client: AsyncClient, register_user: dict, mocker):
    mocker.patch("app.security.access_token_expire_minutes", return_value=-1)
    token = await async_client.post("/token/", json={"email": register_user["email"], "password": register_user["password"]})
    response = await async_client.post("/order/", json={"body": "Test_order"}, headers={"Authorization": f"Bearer {token.json()['token']}"})
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]
    
@pytest.mark.asyncio
async def test_created_order_missing_data(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.post("/order/", json={}, headers={"Authorization": f"Bearer {logged_in_token}"})
    assert response.status_code == 422


# crear la funcion test_get_all_orders
@pytest.mark.asyncio
async def test_get_all_orders():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/order/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0  

# crear test_create_comment
@pytest.mark.asyncio
async def test_create_comment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        comment = {
            "serial": 123,  # replace with a valid serial number
            "comentario": "Test_comment",
            "fecha": "2022-01-01T00:00:00Z",  # replace with the current date/time
            "actualizado_por": "test_user"
        }
        response = await ac.post("/comments/", json=comment)
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["comentario"] == "Test_comment"

@pytest.mark.asyncio
async def test_get_all_comments():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/order_comments/")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)
    for comment in comments:
        assert "serial" in comment
        assert "comentario" in comment
        assert "fecha" in comment
        assert "actualizado_por" in comment

@pytest.mark.asyncio
async def test_get_missing_serial_with_comments():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/order_comments/999999")  # replace with a serial number that does not exist
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_seriales_fastapi():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        cod_men = 1  # Reemplaza esto con un valor de prueba válido
        response = await ac.get(f"/seriales/{cod_men}")
    assert response.status_code == 200
    print(response.json())
    seriales = response.json()
    assert "seriales" in seriales
    assert isinstance(seriales["seriales"], list)