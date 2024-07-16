from fastapi import FastAPI, HTTPException, APIRouter
from typing import Optional, List, Dict
from app.models.seguimiento import EstadoDineroUpdate
from app.routers.function_order import (
    find_serial,
    update_motivo_suborder,
    update_motivo_codmen_order
)
from app.routers.function_money import (
    insertar_estado_dinero,
    serial_existe,
    verificar_dinero,
    actualizar_estado_dinero
)

router = APIRouter()

# Asumiendo que las funciones necesarias están definidas e importadas correctamente

@router.post("/pagos/{serial}")
async def pago_endpoint(
    serial: str,
    cod_men:int,
    valor_consignacion: float,
    actualizado_por: str,
    consignatario: str,
    tipo_de_pago: str):
    # Verificar la existencia del serial
    serial_exists = await find_serial(serial)
    if not serial_exists:
        return {"message": "Serial no encontrado."}
    
    # Verificar la existencia del serial con la función original
    serial_dinero = await serial_existe(serial)
    if serial_dinero:
        return {"message": "El serial ya fue ingresado."}

    # Insertar estado de dinero
    # Asumiendo que la función `insertar_estado_dinero` necesita parámetros adicionales, los cuales deberían ser definidos o obtenidos previamente
    await insertar_estado_dinero(
        serial,
        cod_men=cod_men,
        actualizado_por=actualizado_por,
        consignatario=consignatario,
        valor_consignacion=valor_consignacion,
        tipo_de_pago=tipo_de_pago)

    # Actualizar motivo en suborder_table
    await update_motivo_suborder(serial, nuevo_motivo="e")

    # Actualizar el mensajero y motivo en order_table
    # Asumiendo que la función `update_motivo_men_order` existe y su implementación es similar a las funciones mostradas
    await update_motivo_codmen_order(serial, nuevo_cod_men=cod_men, motivo="e")

    return {"message": "Proceso completado con éxito."}

@router.get("/check-serial-money/{serial}")
async def check_serial_exists(serial: str):
    result = await serial_existe(serial)
    return result


@router.get("/verificar-dinero/", response_model=List[Dict[str, str]])
async def obtener_dinero_verificado(tipo_de_pago: str):
    return await verificar_dinero(tipo_de_pago)
    
# Definir el modelo Pydantic para los datos de entrada

@router.put("/actualizar-estado-dinero/{serial}")
async def update_estado_dinero_endpoint(serial: str, tipo_de_pago: str, verificacion: bool, verificado_por: str, numero_nequi: str):
    try:
        response = await actualizar_estado_dinero(serial, tipo_de_pago, verificacion, verificado_por, numero_nequi)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))