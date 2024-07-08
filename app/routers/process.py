from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from app.database import order_table, comentario_table, database, estado_envio_table, suborder_table
from app.routers.function_order import (
    find_serial,
    find_serial_true,
    find_mensajero,
    find_serial_cajoneras,
    update_motivo_suborder,
    create_cajonera,
    update_motivo_codmen_order,
    create_historial_transacciones,
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

@router.post("/cajoneras/")
async def cajoneras_endpoint(serial: int, cod_men: int, nuevo_motivo: str, actualizado_por: str):
    # 1. Llamar a find_mensajero
    mensajero = await find_mensajero(cod_men)
    if not mensajero:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "El mensajero no existe!!"}
        )
    
    # 1.2 Buscar a el mensajero en la tabla cajoneras
    serial_cajoneras_found = await find_serial_cajoneras(serial)
    if serial_cajoneras_found:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "El serial ya fue ingresado a cajoneras!!"}
        )
        
    # 2. Llamar a find_serial
    serial_found = await find_serial(serial)
    if not serial_found:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Serial no encontrado!!"}
        )

    # 3. Llamar a update_motivo_suborder
    await update_motivo_suborder(serial, nuevo_motivo)

    # 4. Llamar a create_cajonera
    await create_cajonera(serial, cod_men, actualizado_por)

    # 5. Llamar a update_order_from_cajoneras
    await update_motivo_codmen_order(serial, cod_men, motivo='l')

    # 6. Llamar a create_historial_transacciones
    await create_historial_transacciones(serial, "enviado", actualizado_por)

    return {"message": "Proceso exitoso"}

@router.get("/find_serial/{serial}")
async def get_serial(serial: int):
    result = await find_serial_true(serial)
    return result

