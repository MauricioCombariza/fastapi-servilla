import logging
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.database import (
    usuarios_table,
    database,
    mensajeros_table,
    cliente_table
)
from app.security import (
    get_user,
    get_password_hash,
    verify_password,
    get_mensajero
)
from app.models.usuarios import ClienteIn


logger = logging.getLogger(__name__)


async def update_user_password(email: str, old_password: str, new_password: str):
    user = await get_user(email)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "El email no existe!!"}
        )
    if not verify_password(old_password, user.password):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "El password es incorrecto!!"}
        )
    hashed_password = get_password_hash(new_password)
    query = usuarios_table.update().where(usuarios_table.c.email == email).values(password=hashed_password)
    logger.debug(f"Executing: {query}")

    await database.execute(query)
    return {"message": "Password updated"}

async def update_mensajero_password(cod_men: str, old_password: str, new_password: str):
    mensajero = await get_mensajero(cod_men)
    if not mensajero:
        raise HTTPException(status_code=404, detail="Mensajero not found")
    if not verify_password(old_password, mensajero.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    hashed_password = get_password_hash(new_password)
    query = mensajeros_table.update().where(mensajeros_table.c.cod_men == cod_men).values(password=hashed_password)
    logger.debug(f"Executing: {query}")

    await database.execute(query)
    return {"message": "Password updated successfully"}

async def registrar_cliente(cliente_data: ClienteIn):
    query = cliente_table.insert().values(
        nombre=cliente_data.nombre,
        contacto=cliente_data.contacto,
        direccion=cliente_data.direccion,
        telefono=cliente_data.telefono,
        nit=cliente_data.nit,
        email=cliente_data.email,
        password=cliente_data.password,  # Considera hashear la contraseña antes de almacenarla
        permiso=cliente_data.permiso
    )
    logger.debug(f"Executing: {query}")
    cliente_id = await database.execute(query)
    return {"id": cliente_id, **cliente_data.dict()}