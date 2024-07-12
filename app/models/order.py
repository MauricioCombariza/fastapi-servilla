from pydantic import BaseModel, ConfigDict


class Order(BaseModel):
    serial: int
    nombre: str
    direccion: str
    cod_postal: str
    ciudad: str
    id_bodega: int
    barrio: str
    telefono: str
    id_cliente: int
    id_suborden: int
    cod_men: int
    motivo: str
    precio: float
    recaudo: str

class OrderId(Order):
    model_config = ConfigDict(from_attributes= True)
    id: int

class Suborder(BaseModel):
    id: int
    orden: int
    serial: int
    id_cliente: int
    id_bodega: int
    id_producto: int
    cantidad: int
    producto: str
    alias: str
    motivo: str

class CubrimientoBodega(BaseModel):
    id: int
    id_bodega: int
    cod_postal: int


class Producto(BaseModel):
    id: int
    id_cliente: int
    nombre: str
    precio: float

class ProductSummary(BaseModel):
    id_producto: int
    alias: str
    total_cantidad: int

