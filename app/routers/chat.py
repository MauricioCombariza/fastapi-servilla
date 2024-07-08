from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from app.database import (
    order_table,
    cajoneras_table
    )
# from app.routers.function_chat import (
#     table_to_dataframe,
#     process_and_send_messages,
#     update_cajoneras_from_whatsapp
#     )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

table_mapping = {
    "order_table": order_table,
    "cajoneras_table": cajoneras_table,
    # Añade más mapeos según sea necesario
}

# @router.get("/crear-df")
# async def endpoint_crear_df(table_name: str):
#     table = table_mapping.get(table_name)
#     await table_to_dataframe(table)
#     return {"message": "DataFrame creado y mostrado en consola"}

# eliminando whatsapp

# @router.post("/enviar_mensajes/")
# async def enviar_mensajes():
#     try:
#         await process_and_send_messages()
#         return {"mensaje": "Mensajes enviados exitosamente"}
#     except Exception as e:
        # return {"error": str(e)}

# Sin whatsapp


@router.put("/update-cajoneras/{serial}")
async def update_cajoneras_endpoint(serial: int):
    # try:
    #     result = await update_cajoneras_from_whatsapp(serial)
    #     return result
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    result = await update_cajoneras_from_whatsapp(serial)
    return result