from jose import jwt
from fastapi import Depends, HTTPException, status
from app.config import supabase
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.sql import update
import logging
from app.database import (
    order_table,
    comentario_table,
    database,
    estado_envio_table,
    suborder_table,
    mensajeros_table,
    historial_transacciones_table,
    cajoneras_table)
from app.models.order import Order, OrderId
from datetime import datetime
from app.models.seguimiento import Comentario, ComentarioId, Cajoneras
# from app.columns import column_names
from sqlalchemy import select, func, delete
import pandas as pd
import re
from dotenv import load_dotenv
import os
import sys
sys.setrecursionlimit(2000)  # Aumenta el límite de profundidad de recursión

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def create_order_function(order: Order):
    data = order.model_dump()
    query = order_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

async def find_serial_true(serial: str):
    query = order_table.select().where(order_table.c.serial == serial)
    result = await database.fetch_one(query)
    return {"ok": result is not None}

async def find_serial(serial: str):
    query = order_table.select().where(order_table.c.serial == serial)
    return await database.fetch_one(query)

async def find_serial_cajoneras(serial: str):
    query = cajoneras_table.select().where(cajoneras_table.c.serial == serial)
    return await database.fetch_one(query)

async def create_new_comments_function(comentario: Comentario):
    serial = await find_serial(comentario.serial)
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")
    data = comentario.model_dump()
    query = comentario_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

async def get_comments_by_serial_function(serial: str):
    query = comentario_table.select().where(comentario_table.c.serial == serial)
    return await database.fetch_all(query)

# funcion asincrona que recibe un cod_men y retorna los seriales de la tabla estado_envio donde cod_men == cod_men y estado_envio sea diferente de E o de D
async def get_seriales_pendientes_por_mensajero(cod_men):
    query = """
    SELECT serial
    FROM estado_envio
    WHERE cod_men = ? AND estado_envio NOT IN ('E', 'D', 'e', 'd')
    """
    async with estado_envio_table.execute(query, [cod_men]) as cursor:
        seriales = [row[0] for row in await cursor.fetchall()]
    return seriales

async def print_table_as_dataframe(table_name: str):
    # Construir la consulta SQL
    query = f"SELECT * FROM {table_name}"
    
    # Ejecutar la consulta y obtener los resultados
    results = await database.fetch_all(query)
    
    # Convertir los resultados en un DataFrame de pandas
    df = pd.DataFrame(results)
    
    # Imprimir el DataFrame
    print(df)

    

async def get_last_id(table_name: str):
    response = supabase.table(table_name).select("id").order("id", desc=True).limit(1).execute()

    if response.data:
        max_id = response.data[0]['id']
        return max_id
    else:
        # Si no se encontraron datos, retornar una lista vacía
        return 0


    
def add_serial_numbers(last_id, df):
    # Asegúrate de que el índice del DataFrame comience en 1 si es necesario
    df.reset_index(drop=True, inplace=True)
    
    # Calcula el serial para cada fila y lo añade como una nueva columna
    df['serial'] = df.index + 1 + last_id + 7210000000
    
    return df
    
async def check_order_and_update_df(order_number, df):
    # Check for existing order using a more efficient query
    
    response = supabase.table("orders").select("*").eq("orden", order_number).execute()
    print(response)
    if len(response.data) > 0:
        return "Order number already exists."
    else:
      # Update DataFrame with order number
      df['orden'] = order_number
    #   print(df)
      return df
          
async def rename_and_adjust_columns(df, client_number):
    response = supabase.table("columns").select("*").eq("id_cliente", client_number).execute()
    if len(response.data)==0:
        print(f"Cliente {client_number} no encontrado.")
        return df  # Return the original DataFrame if there's an error
    print(df.columns)
    data = response.data
    column_names = pd.DataFrame(data)
    rename_dict = dict(zip(column_names['actual_name'], column_names['name']))
    df.rename(columns=rename_dict, inplace=True)

    column_order = [
        'id_cliente', 'orden', 'serial', 'id_guia', 'nombre', 'ciudad',
        'id_bodega', 'direccion', 'telefono', 'f_emi', 'forma_de_pago',
        'recaudo', 'contenido'
    ]
    df = df[column_order]
    return df

async def insert_df_into_table(table_name: str, df: pd.DataFrame):
    for column in ['id_guia', 'serial', 'telefono']:
        if column in df.columns:
            df[column] = df[column].astype(str)

    list_of_dicts = df.to_dict(orient="records")
    response = supabase.table(table_name).insert(list_of_dicts).execute()

    if len(response.data) == 0:
        print(f"Error inserting data: {response.error}")
    else:
        print(f"Data inserted successfully: {response.data}")

def expandir_contenido(row):
    # Extrae todas las secuencias de 'cantidad * producto.' de 'contenido'
    matches = re.findall(r'(\d+) \* ([^.]+)\.', row['contenido'])

    # Crea una nueva fila por cada secuencia de 'cantidad * producto.'
    nuevas_filas = []
    for cantidad, producto in matches:
        cantidad = int(cantidad)
        # Si aparece la palabra 'Dúo', multiplica la cantidad por dos y borra la palabra 'Dúo'
        if 'Dúo' in producto:
            cantidad = cantidad * 2
            producto = producto.replace('Dúo', '').strip()

        # Si aparece la palabra 'Crema', borra la palabra 'Crema'
        if 'Crema' in producto:
            producto = producto.replace('Crema', '').strip()

        nuevas_filas.append({'serial': row['serial'], 'cantidad': cantidad, 'producto': producto})

    return nuevas_filas


async def agregar_producto(cliente: int, df: pd.DataFrame, orden: int) -> pd.DataFrame:
    response = supabase.table("products").select("*").eq("id_cliente", cliente).execute()
    # print(response.data)
    if len(response.data) == 0:
        print(f"Error fetching data: {response.error}")
        return df  # Return the original DataFrame if there's an error
    # print("df: ", df)
    data = response.data
    df_producto = pd.DataFrame(data)
    df_producto = df_producto[df_producto['id_cliente'] == cliente]
    # print("df_producto: ", df_producto.columns)
    df = df.copy()
    df['id_producto'] = df['producto'].apply(lambda x: buscar_producto(x, df_producto))
    df['alias'] = df['producto'].apply(lambda x: buscar_alias(x, df_producto))
    df['id_cliente'] = cliente
    df['orden'] = orden
    df['estado'] = 'j'
    df['id_producto'] = df['id_producto'].astype(int)
    df['id_cliente'] = df['id_cliente'].astype(int)
    df['orden'] = df['orden'].astype(int)
    # print(df)
    return df

def buscar_producto(producto, df_producto):
    for palabra in producto.split():
        if palabra in df_producto['producto'].values:
            return df_producto.loc[df_producto['producto'] == palabra, 'id_producto'].values[0]
    raise ValueError(f"No se encontró el producto '{producto}' en df_producto")

def buscar_alias(producto, df_producto):
    for palabra in producto.split():
        if palabra in df_producto['producto'].values:
            return df_producto.loc[df_producto['producto'] == palabra, 'alias'].values[0]
    raise ValueError(f"No se encontró el producto '{producto}' en df_producto")

async def get_order_summary(order_id, db):
    try:
        response = (
            supabase.table("suborders")
            .select("orden", "id_producto", "alias", "cantidad")
            .eq("orden", order_id)
            .execute()
        )
        # Verificar si la respuesta contiene datos
        if response.data:
            logging.info(f"Query results: {response.data}")

            # Convertir los resultados en una lista de diccionarios
            diccionario = [dict(row) for row in response.data]
            # Convertir el diccionario en un DataFrame
            df = pd.DataFrame(diccionario)
            # Hacer un pivot table que muestre las columnas 'id_producto' y 'alias' y sume la columna 'cantidad'
            df = df.pivot_table(index='alias', values='cantidad', aggfunc='sum', fill_value=0)
            df = df.reset_index()
            return df.to_dict(orient="records")
        else:
            logging.info("No data found for the given order_id.")
            return []
        # Crear una consulta para obtener todos los datos de suborder_table
        # # query = select(suborder_table.c).where(suborder_table.c.orden == order_id)
        # logging.info(f"Executing query: {query}")

        # # Ejecutar la consulta y obtener todos los resultados
        # rows = await db.fetch_all(query)
        # logging.info(f"Query results: {rows}")

        
        # # Convertir los resultados en una lista de diccionarios
        # diccionario = [dict(row) for row in rows]
        # # Convertir el diccionario en un DataFrame
        # df = pd.DataFrame(diccionario)
        # # Hacer un pivot table que muestre las columnas 'id_producto' y 'alias' y sume la columna 'cantidad'
        # df = df.pivot_table(index='alias', values='cantidad', aggfunc='sum', fill_value=0)
        # df = df.reset_index()
        # return df.to_dict(orient="records")


    except Exception as e:
        logging.error(f"Error getting order summary: {e}")
        raise    

# funcion asincrona que reciba un cod_men y verifique si existe en la tabla mensajeros
async def find_mensajero(mensajero: int):
    # return mensajero
    query = select(mensajeros_table).where(mensajeros_table.c.cod_men == mensajero)
    return await database.fetch_one(query)
   

async def create_cajonera(serial: str, cod_men: int, actualizado_por: str):
    # Crear la consulta SQL para insertar en la tabla cajoneras
    data = {"serial": serial, "cod_men": cod_men, "fecha": datetime.now(), "envio_whatsApp": False, "actualizado_por": actualizado_por}
    query = (
        cajoneras_table.insert().
        values(**data)
    )

    # Ejecutar la consulta SQL
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

async def create_historial_transacciones(serial: str, estado_envio: str, actualizado_por: str):
    # Crear la consulta SQL para insertar en la tabla historial_transacciones_table
    data = {"serial": serial, "estado_envio": estado_envio, "fecha_actualizacion": datetime.now(), "actualizado_por": actualizado_por}
    query = (
        historial_transacciones_table.insert().
        values(**data)
    )

    # Ejecutar la consulta SQL
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

async def update_motivo_suborder(serial: str, nuevo_motivo: str):
    # Crear la consulta SQL para actualizar el motivo en la tabla suborder_table
    query = (
        update(suborder_table).
        where(suborder_table.c.serial == serial).
        values(motivo=nuevo_motivo)
    )

    # Ejecutar la consulta SQL
    await database.execute(query)
    return {"serial": serial, "motivo": nuevo_motivo}

async def update_motivo_codmen_order(serial: str, nuevo_cod_men: int, motivo: str):
    # Crear la consulta SQL para actualizar el cod_men y motivo en la tabla order_table
    query = (
        update(order_table).
        where(order_table.c.serial == serial).
        values(cod_men=nuevo_cod_men, motivo=motivo)
    )

    # Ejecutar la consulta SQL
    await database.execute(query)
    return {"serial": serial, "cod_men": nuevo_cod_men, "motivo": motivo}


async def eliminar_orden_por_numero(orden: int):
    # Construir la consulta de eliminación
    query = delete(order_table).where(order_table.c.orden == orden)
    async with database.transaction():
        # Ejecutar la consulta dentro del contexto de transacción
        result = await database.execute(query)
        
        # No es necesario llamar a commit o rollback explícitamente
        # El contexto de transacción maneja esto automáticamente
        
        # Retornar el número de filas afectadas
        # Nota: La propiedad rowcount puede no estar disponible dependiendo del driver de base de datos
        return {"message": f"{result} filas eliminadas."}
    
    
async def eliminar_suborden_por_numero(orden: int):
    # Construir la consulta de eliminación
    query = delete(suborder_table).where(suborder_table.c.orden == orden)
    async with database.transaction():
        # Ejecutar la consulta dentro del contexto de transacción
        result = await database.execute(query)
        
        # No es necesario llamar a commit o rollback explícitamente
        # El contexto de transacción maneja esto automáticamente
        
        # Retornar el número de filas afectadas
        # Nota: La propiedad rowcount puede no estar disponible dependiendo del driver de base de datos
        return {"message": f"{result} filas eliminadas."}
    