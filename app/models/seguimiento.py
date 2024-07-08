from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime
from app.models.order import Order

class Cajoneras(BaseModel):
    model_config = ConfigDict(from_attributes= True)
    serial: int
    cod_men: int 
    fecha: datetime
    actualizado_por: str
    envio_whatsApp: bool

class CajonerasId(Cajoneras):
    model_config = ConfigDict(from_attributes= True)
    id: int

class Historial_transacciones(BaseModel):
    model_config = ConfigDict(from_attributes= True)
    serial: int
    estado_envio: str
    fecha_actualizacion: datetime
    actualizado_por: str

class Historial_transaccionesId(Historial_transacciones):
    model_config = ConfigDict(from_attributes= True)
    id: int

class Comentario(BaseModel):
    serial: int
    comentario: str
    fecha: datetime
    actualizado_por: str

class ComentarioId(Comentario):
    model_config = ConfigDict(from_attributes= True)
    id: int

class Comentario_envio(BaseModel):
    post: Order
    comentario: List[Comentario]

class Estado_envio(BaseModel):
    id: int
    serial: int
    estado: str
    fecha: datetime
    actualizado_por: str

class Estado_dinero(BaseModel):
    id: int
    serial: int
    cod_men: int
    estado: str
    fecha: datetime
    actualizado_por: str
    consignatario: str
    fecha_consignacion: datetime
    valor_consignacion: float
    tipo_de_pago: str
    verificacion_pago: bool
    verificado_por: str
    numero_nequi: str
    transferido: bool
    banco_transferencia: str
    numero_transferencia: str
    fecha_transferencia: datetime

class Verificacion_dinero(BaseModel):
    id: int
    serial: int
    estado: str
    fecha: datetime
    actualizado_por: str
    consignatario: str
    fecha_consignacion: datetime
    valor_consignacion: float
    imagen: str

class EstadoDineroUpdate(BaseModel):
    verificacion: bool
    verificado_por: str
    numero_nequi: str
