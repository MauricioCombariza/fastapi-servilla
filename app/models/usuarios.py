from pydantic import BaseModel, Field

class MensajerosLogin(BaseModel):
    cod_men: int
    password: str

class Mensajeros(MensajerosLogin):
    nombre: str
    direccion: str
    email: str
    sector: str
    telefono: str
    id_bodega: int
    permiso: bool

class MensajerosIn(Mensajeros):
    id: int

class UsuariosLogin(BaseModel):
    email: str
    password: str

class UsuariosUpdate(UsuariosLogin):
    new_password: str

class Usuarios(UsuariosUpdate):
    nombre: str = Field(..., example="Your Name")
    direccion: str = Field(..., example="Your Address")
    telefono: str = Field(..., example="Your Phone")
    id_bodega: int = Field(..., example=1)
    rol: int = Field(..., example=1)
    permiso: bool = Field(..., example=True)
        

class UsuariosIn(Usuarios):
    id: int

class Cliente(BaseModel):
    nombre: str
    contacto: str
    direccion: str
    telefono: str
    nit: str
    email: str
    password: str
    permiso: bool

class ClienteIn(Cliente):
    id: int

class Bodega(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    permiso: bool
    email: str
    password: str

class BodegaIn(Bodega):
    id: int