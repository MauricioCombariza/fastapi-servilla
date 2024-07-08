import pytest
from app import security

def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30, "Access token should expire in 30 minutes"

def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123"}.items() <= security.jwt.decode(
        token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        ).items(), "Token should be created"

def test_password_hashes():
    password = "123"
    hashed_password = security.get_password_hash(password)
    assert security.verify_password(password, hashed_password), "Password should be verified"

@pytest.mark.anyio
async def test_get_user(register_user: dict):
    user = await security.get_user(register_user["email"], security.usuarios_table)
    assert user is not None, "User should not be None"
    assert user["email"] == register_user["email"]
    
@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@example.com", security.usuarios_table)
    assert user is None

@pytest.mark.anyio
async def test_authenticate_user(register_user: dict):
    user = await security.authenticate_user(
        register_user["email"], register_user["password"], security.usuarios_table
        )
    assert user is not None, "User should not be None"
    assert user["email"] == register_user["email"]

@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.com", "123", security.usuarios_table)

@pytest.mark.anyio
async def test_authenticate_user(register_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(register_user["email"], "wrong_password", security.usuarios_table)

@pytest.mark.anyio
async def test_get_current_user(register_user: dict):
    token = security.create_access_token(register_user["email"])
    user = await security.get_current_user(token, security.usuarios_table)
    assert user is not None, "User should not be None"
    assert user["email"] == register_user["email"]

@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalid_token", security.usuarios_table)