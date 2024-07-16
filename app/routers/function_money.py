from datetime import datetime
from app.database import estado_dinero_table, database


async def insertar_estado_dinero(
        serial: str,
        cod_men: int,
        actualizado_por: str,
        consignatario: str,
        valor_consignacion: float,
        tipo_de_pago: str):
    query = estado_dinero_table.insert().values(
        serial=serial,
        estado='e',
        cod_men=cod_men,
        fecha=datetime.now(),
        actualizado_por=actualizado_por,
        consignatario=consignatario,
        fecha_consignacion=datetime.now(),
        valor_consignacion=valor_consignacion,
        tipo_de_pago=tipo_de_pago,
        verificacion_pago=False,
        verificado_por='',
        numero_nequi=''
    )
    last_record_id = await database.execute(query)
    return {"id": last_record_id, "message": "Estado de dinero insertado correctamente"}

async def serial_existe(serial: str) -> bool:
    query = estado_dinero_table.select().where(estado_dinero_table.c.serial == serial)
    result = await database.fetch_one(query)
    return result is not None

async def verificar_dinero(tipo_de_pago: str):
    query = estado_dinero_table.select().with_only_columns(
        estado_dinero_table.c.consignatario,
        estado_dinero_table.c.cod_men,
        estado_dinero_table.c.serial,
        estado_dinero_table.c.valor_consignacion
    ).where(
        (estado_dinero_table.c.estado == 'e') &
        (estado_dinero_table.c.tipo_de_pago == tipo_de_pago)
    )
    result = await database.fetch_all(query)
    result_dicts = [
        {
            'consignatario': record['consignatario'],
            'cod_men': (record['cod_men']),
            'serial': str(record['serial']),
            'valor_consignacion': (record['valor_consignacion'])
        } for record in result
    ]
    return result_dicts

    

async def actualizar_estado_dinero(serial: str, tipo_de_pago: str, verificacion: bool, verificado_por: str, numero_nequi: int):
    query = estado_dinero_table.update().\
        where(
            (estado_dinero_table.c.serial == serial) &
            (estado_dinero_table.c.tipo_de_pago == tipo_de_pago)
        ).\
        values(
            verificacion_pago=verificacion,
            verificado_por=verificado_por,
            numero_nequi=numero_nequi,
            estado='E'
        )
    result = await database.execute(query)
    if result:
        return {"message": "Estado de dinero actualizado correctamente"}
    else:
        return {"message": "No se encontró una fila que coincida con los criterios especificados"}
