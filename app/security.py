import logging
import datetime
from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from app.database import database, usuarios_table, cliente_table, mensajeros_table, bodega_table
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def access_token_expire_minutes() -> int:
    return ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(email: str):
    logger.debug(f"Creating access token for {email}")
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expire_minutes())
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token_mensajero(cod_men: int):
    logger.debug(f"Creating access token for {cod_men}")
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expire_minutes())
    jwt_data = {"sub": cod_men, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    query = usuarios_table.select().where(usuarios_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result

async def get_mensajero(codigo: int):
    query = usuarios_table.select().where(usuarios_table.c.cod_men == codigo)
    result = await database.fetch_one(query)
    if result:
        return result

async def authenticate_user(email: str, password: str):
    logger.debug(f"Authenticating user {email}")
    user = await get_user(email)
    if not user:
        raise credentials_exception
    if not verify_password(password, user["password"]):
        raise credentials_exception
    if not user["permiso"]:
        raise credentials_exception
    return user

async def authenticate_mensajero(codigo: int, password: str):
    logger.debug(f"Authenticating user {codigo}")
    user = await get_mensajero(codigo)
    if not user:
        raise credentials_exception
    if not verify_password(password, user["password"]):
        raise credentials_exception
    if not user["permiso"]:
        raise credentials_exception
    return user

async def get_user_role(email: str):
    query = usuarios_table.select().where(usuarios_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result["rol"]
    
async def get_user_username(email: str):
    query = usuarios_table.select().where(usuarios_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result["nombre"]


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            ) from e
    except JWTError as e:
        raise credentials_exception from e
    user = await get_user(email, usuarios_table)
    if user is None:
        raise credentials_exception
    return user

async def get_mensajero(cod_men: int):
    query = mensajeros_table.select().where(mensajeros_table.c.cod_men == cod_men)
    result = await database.fetch_one(query)
    if result:
        return result