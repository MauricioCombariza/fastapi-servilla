from fastapi import HTTPException
from typing import List
from datetime import datetime, timedelta
from pywhatkit import sendwhatmsg_instantly
import pandas as pd
from sqlalchemy import select
from sqlalchemy.sql import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import (
    cajoneras_table,
    order_table,
    database
)

async def table_to_dataframe(table_name: str):
    """
    Convierte una tabla de SQLAlchemy a un DataFrame de pandas.

    """
    # Ejecutar la consulta para obtener todos los registros de la tabla
    query = select(table_name)
    result = await database.fetch_all(query)

    # Convertir el resultado a una lista de diccionarios
    data = [dict(row) for row in result]

    # Crear un DataFrame de pandas
    df = pd.DataFrame(data)
    print(df)

    return df

async def df_whatsapp_messages():
    # Paso 1: Crear DataFrames a partir de las tablas
    df_order = await table_to_dataframe(order_table)
    df_cajoneras = await table_to_dataframe(cajoneras_table)

    # Paso 2: Filtrar df_cajoneras donde envio_whatsApp sea igual a 0
    df_cajoneras_filtrado = df_cajoneras[df_cajoneras['envio_whatsApp'] == False]

    # Paso 3: Realizar un left join de df_cajoneras_filtrado con df_order
    # Asumiendo que 'serial' es la columna común para el join
    df_final = pd.merge(df_cajoneras_filtrado, df_order, on=['serial', 'cod_men'], how='inner')
    columnas_df_order = ['serial', 'nombre', 'cod_men','id_cliente','direccion', 'telefono', 'forma_pago', 'recaudo', 'contenido', 'forma_de_pago']  
    df_final = df_final.filter(items=columnas_df_order)


    print(df_final.columns)

    # Paso 4: df_final es el DataFrame resultante
    return df_final

    # Calcular las fechas de entrega (mañana y pasado mañana

    
async def process_and_send_messages():
    # Read the DataFrame from Excel file
    # df = pd.read_excel('../libros/base_envios.xlsx')
    df = await df_whatsapp_messages()

    # Get the current date
    fecha_actual = datetime.now()

    # Calculate delivery dates (tomorrow and day after tomorrow)
    fecha_entrega_manana = fecha_actual + timedelta(days=1)
    fecha_entrega_pasado_manana = fecha_actual + timedelta(days=3)

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Construct the message for each row
        phone_number = "+57" + str(row['telefono'])
        serial=row['serial']
        message = f"""
        Hola **{row['nombre']}**,

        gracias por tu compra a ** {row['id_cliente']} **

        Tu pedido, número **{row['serial']}/{row['cod_men']}**, contiene: **{row['contenido']}**.

        Será entregado en **{row['direccion']}** para un pago tipo **{row['forma_de_pago']}**, por un valor de **{row['recaudo']}**.

        El producto será entregado entre el {fecha_entrega_manana.strftime('%d/%m')} y el {fecha_entrega_pasado_manana.strftime('%d/%m')}.


        Recuerda que puedes pagarnos por Nequi al celular **3125213058** y enviar por WhatsApp el nombre del cliente y el nombre de la persona que hace la transferencia.

        Si tienes alguna novedad, escríbenos a este número.
        """

        # Send the message using pywhatkit
        sendwhatmsg_instantly(phone_number, message, 15, True, 3)
        print("seial",serial)
        await update_cajoneras_from_whatsapp(serial)

        print(f"Mensaje enviado a {phone_number}")

    # print("Mensajes enviados exitosamente")


async def update_cajoneras_from_whatsapp(serial: int):
    # Crear la consulta SQL para actualizar la columna envio_whatsapp en la tabla cajoneras_table
    query = (
        update(cajoneras_table).
        where(cajoneras_table.c.serial == serial).
        values(envio_whatsApp=True)
    )

    # Ejecutar la consulta SQL
    await database.execute(query)
    return {"serial": serial, "envio_whatsApp": True}