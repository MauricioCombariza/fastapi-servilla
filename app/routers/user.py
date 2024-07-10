
import logging 
from fastapi import APIRouter, HTTPException, Body, status
from fastapi.responses import JSONResponse
from app.models.usuarios import (
    Usuarios,
    Cliente,
    Mensajeros,
    Bodega,
    UsuariosLogin,
    MensajerosLogin
) 
from app.database import usuarios_table, database, mensajeros_table, bodega_table
from app.security import (
    get_user,
    get_password_hash,
    authenticate_user,
    authenticate_mensajero,
    create_access_token,
    get_user_role,
    get_user_username,
    get_mensajero,
    create_access_token_mensajero,
    )
from app.routers.function_users import (
    update_user_password,
    update_mensajero_password,
    registrar_cliente,
    registrar_bodega
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register/", status_code=201)
async def register_user(user: Usuarios):
   if user.password != user.new_password:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Error en el password"}
        )
   if await get_user(user.email):
               return JSONResponse(
            status_code=status.HTTP_400_NOT_FOUND,
            content={"detail": "El usuario ya existe!!"}
        )
   hashed_password = get_password_hash(user.password)
   query = usuarios_table.insert().values(email=user.email, password=hashed_password, nombre=user.nombre, direccion=user.direccion, telefono=user.telefono, rol=user.rol, permiso=user.permiso)
   logger.debug(f"Executing: {query}")

   await database.execute(query)
   return {"message": "User created"}

@router.post("/token/")
async def login(user: UsuariosLogin):
    try:
        user_authenticated = await authenticate_user(user.email, user.password)
        if not user_authenticated:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Credenciales invalidas!!"}
        )
        
        access_token = create_access_token(user_authenticated["email"])
        username = await get_user_username(user_authenticated["email"])
        return {"token": access_token, "token_type": "bearer", "username": username, "rol": user_authenticated["rol"]}
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Credenciales invalidas!!"}
        )
    
@router.post("/token_mensajeros/")
async def login_mensajeros(user: MensajerosLogin):
    user = await authenticate_mensajero(user.cod_men, user.password)
    if user:
        isValid = True
    access_token = create_access_token_mensajero(user["cod_men"])
    username = await get_user_username(user["email"])
    return {"token": access_token, "token_type": "bearer", "username": username, isValid: isValid}


# crear una function asincrona para ingresar Mensajeros en la tabla mensajeros usando schema MensajerosIn
@router.post("/register_mensajeros/", status_code=201)
async def register_mensajeros(mensajero: Mensajeros):
    if await get_mensajero(mensajero.cod_men):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(mensajero.password)
    query = mensajeros_table.insert().values(email=mensajero.email, password=hashed_password, nombre=mensajero.nombre, direccion=mensajero.direccion, telefono=mensajero.telefono, cod_men=mensajero.cod_men, permiso=mensajero.permiso, sector=mensajero.sector)
    logger.debug(f"Executing: {query}")

    await database.execute(query)
    return {"message": "El operado de ruta ha sido creado en forma exitosa!!"}


@router.post("/update-password")
async def update_password_endpoint(email: str = Body(...), old_password: str = Body(...), new_password: str = Body(...)):
    return await update_user_password(email, old_password, new_password)

@router.post("/update-mensajero-password")
async def update_mensajero_password_endpoint(cod_men: str = Body(...), old_password: str = Body(...), new_password: str = Body(...)):
    return await update_mensajero_password(cod_men, old_password, new_password)

@router.post("/register-clientes/", status_code=status.HTTP_201_CREATED)
async def crear_cliente(cliente_data: Cliente):
    try:
        cliente_creado = await registrar_cliente(cliente_data)
        return cliente_creado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/bodegas/", response_model=Bodega, status_code=status.HTTP_201_CREATED)
async def create_bodega(bodega_data: Bodega):
    try:
        # Llama a la función registrar_bodega y pasa los datos de la bodega
        result = await registrar_bodega(bodega_data)
        return result
    except Exception as e:
        logging.error(f"Error al registrar bodega: {e}")
        raise HTTPException(status_code=400, detail="Error al registrar la bodega")
