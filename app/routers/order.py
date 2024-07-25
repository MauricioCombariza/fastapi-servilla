import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, File, UploadFile, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Table, MetaData, select, func
from app.models.order import Order, OrderId, ProductSummary, Suborder
from app.models.usuarios import UsuariosIn
from app.database import database, order_table, comentario_table, suborder_table
from app.models.seguimiento import Comentario, ComentarioId, Comentario_envio
from app.routers.function_order import (
    get_order_summary,
    expandir_contenido,
    agregar_producto,
    get_last_id,
    add_serial_numbers,
    insert_df_into_table,
    check_order_and_update_df,
    rename_and_adjust_columns,
    create_new_comments_function,
    get_comments_by_serial_function,
    get_seriales_pendientes_por_mensajero,
    eliminar_orden_por_numero,
    eliminar_suborden_por_numero,
    print_table_as_dataframe,
)
from typing import List
import pandas as pd
from io import BytesIO
import unidecode
from app.models.usuarios import UsuariosIn
from app.security import get_current_user, oauth2_scheme

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create_order/")
async def create_order(order_number: int, id_cliente: int, file: UploadFile = File(...)):
    order_number_int = int(order_number)
    id_cliente_int = int(id_cliente)
    logger.info(f"Processing file for order {order_number_int}")
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return JSONResponse(status_code=400, content={"message": "This API only accepts Excel files."})
    
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        logger.debug("DataFrame columns after reading Excel: %s", df.columns)

        last_id = await get_last_id('orders')
        df = add_serial_numbers(last_id, df)
        df_updated = await check_order_and_update_df(order_number_int, df)        
                
        if isinstance(df_updated, str):
            return JSONResponse(status_code=400, content={"message": df_updated})
        
        df_updated1 = rename_and_adjust_columns(df_updated, id_cliente_int)
        logger.debug("DataFrame columns after renaming and adjusting: %s", df_updated1.columns)
        # Antes de la primera inserción
        print(f"Pre-insert check for order_table: {df_updated1.dtypes}")

        # Ajuste: Mover la limpieza y conversión para después de obtener df_updated1 y aplicarlo a df_updated1
        if 'recaudo' in df_updated1.columns:
            # Primero, elimina el símbolo del dólar y cualquier otro carácter no numérico excepto la coma
            df_updated1['recaudo'] = df_updated1['recaudo'].replace({'\$': '', '\.': ''}, regex=True)
            # Luego, reemplaza las comas por puntos para adecuar el formato decimal
            df_updated1['recaudo'] = df_updated1['recaudo'].replace({',': '.'}, regex=True).astype(float)
        else:
            # Opcional: Maneja el caso de que 'recaudo' no exista en df_updated1, por ejemplo, asignando un valor predeterminado
            df_updated1['recaudo'] = 0.0  # Asigna un valor

        await insert_df_into_table('orders', df_updated1)
        nuevas_filas = []
        for _, row in df_updated1.iterrows():
            nuevas_filas.extend(expandir_contenido(row))
            
        df_inventario = pd.DataFrame(nuevas_filas)
        df_inventario['producto'] = df_inventario['producto'].str.lower().apply(unidecode.unidecode)
        df_inventario = agregar_producto(cliente=id_cliente_int, df=df_inventario, orden=order_number_int)

        print(f"Pre-insert check for suborder_table: {df_inventario.dtypes}")
        logger.debug(f"Dataframe: {df_inventario.head()}")
        await insert_df_into_table('suborders', df_inventario)
        
        return {"message": "File processed successfully", "data": df_updated.head().to_dict()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        await file.close()


@router.post("/comments/", response_model=ComentarioId, status_code=201)
async def create_new_comments(comentario: Comentario, current_user: Annotated[UsuariosIn, Depends(get_current_user)]):
    logger.info(f"Creating new comment: {comentario}")
    new_comment = await create_new_comments_function(comentario)
    logger.debug(f"New comment: {new_comment}")
    return new_comment

@router.get("/order/", response_model=List[OrderId])
async def read_orders():
    logger.info("Reading all orders")
    query = order_table.select()
    logger.debug(f"Query: {query}")
    return await database.fetch_all(query)

@router.get("/order_comments/", response_model=List[Comentario])
async def get_all_comments():
    logger.info("Reading all comments")
    query = comentario_table.select()
    logger.debug(f"Query: {query}")
    return await database.fetch_all(query)
    

@router.get("/serial/{serial}/comment", response_model=List[Comentario])
async def get_comments_by_serial(serial: str):
    logger.info(f"Getting comments for serial {serial}")
    comentarios = await get_comments_by_serial_function(serial)
    logger.debug(f"Comentarios: {comentarios}")
    return comentarios


@router.get("/seriales/{cod_men}")
async def get_seriales_fastapi(cod_men: int):
    logger.info(f"Getting serial numbers for messenger")
    try:
        seriales = await get_seriales_pendientes_por_mensajero(cod_men)
        logger.debug(f"Seriales: {seriales}")
        return {"seriales": seriales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/order_summary/{order_id}", response_model=List[dict])
async def order_summary(order_id: int):
    logger.info(f"Getting summary for order {order_id}")
    try:
        # Llamar a la función get_order_summary
        df = await get_order_summary(order_id, database)
        logger.debug(f"Dataframe: {df}")
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/orden/{orden_id}")
async def eliminar_orden_y_suborden(orden_id: int):
    try:
        # Llama a la función para eliminar la orden principal
        resultado_orden = await eliminar_orden_por_numero(orden_id)
        
        # Llama a la función para eliminar las subordenes asociadas
        resultado_suborden = await eliminar_suborden_por_numero(orden_id)
        
        # Si ambas operaciones son exitosas, devuelve un mensaje de éxito
        return {"message": "Orden y subordenes eliminadas correctamente."}
    except Exception as e:
        # En caso de error, devuelve un mensaje de error
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/print-table/{table_name}")
async def endpoint_print_table_as_dataframe(table_name: str):
    await print_table_as_dataframe(table_name)
    return {"message": f"Printed {table_name} as DataFrame"}