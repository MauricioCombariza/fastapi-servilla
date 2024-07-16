import databases
import sqlalchemy
from app.config import config

metadata = sqlalchemy.MetaData()

cliente_table = sqlalchemy.Table(
    "clientes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("contacto", sqlalchemy.String),
    sqlalchemy.Column("direccion", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("nit", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("permiso", sqlalchemy.Boolean),
)

bodega_table = sqlalchemy.Table(
    "bodegas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("direccion", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("permiso", sqlalchemy.Integer),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
)

product_table = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_cliente", sqlalchemy.Integer),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("precio", sqlalchemy.Float),
)

mensajeros_table = sqlalchemy.Table(
    "mensajeros",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_bodega", sqlalchemy.Integer),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("direccion", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("sector", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("cod_men", sqlalchemy.Integer, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("permiso", sqlalchemy.Boolean),
)

order_table = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("orden", sqlalchemy.Integer),
    sqlalchemy.Column("id_guia", sqlalchemy.String),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("direccion", sqlalchemy.String),
    sqlalchemy.Column("id_bodega", sqlalchemy.Integer),
    sqlalchemy.Column("cod_postal", sqlalchemy.Integer),
    sqlalchemy.Column("barrio", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("ciudad", sqlalchemy.String),
    sqlalchemy.Column("f_emi", sqlalchemy.DateTime),
    sqlalchemy.Column("cod_men", sqlalchemy.Integer),
    sqlalchemy.Column("motivo", sqlalchemy.String),
    sqlalchemy.Column("id_cliente", sqlalchemy.Integer),
    sqlalchemy.Column("forma_de_pago", sqlalchemy.String),
    sqlalchemy.Column("recaudo", sqlalchemy.Float),
    sqlalchemy.Column("contenido", sqlalchemy.String),
)

suborder_table = sqlalchemy.Table(
    "suborders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("orden", sqlalchemy.Integer),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("id_cliente", sqlalchemy.Integer),
    sqlalchemy.Column("id_bodega", sqlalchemy.Integer),
    sqlalchemy.Column("id_producto", sqlalchemy.Integer),
    sqlalchemy.Column("cantidad", sqlalchemy.Integer),
    sqlalchemy.Column("producto", sqlalchemy.String),
    sqlalchemy.Column("alias", sqlalchemy.String),
    sqlalchemy.Column("motivo", sqlalchemy.String),
)

product_table = sqlalchemy.Table(
    "cubrimiento_bodegas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_bodega", sqlalchemy.Integer),
    sqlalchemy.Column("cod_postal", sqlalchemy.Integer),
)


usuarios_table = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("direccion", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("id_bodega", sqlalchemy.Integer),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("new_password", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("rol", sqlalchemy.Integer),
    sqlalchemy.Column("permiso", sqlalchemy.Boolean),
)



cajoneras_table = sqlalchemy.Table(
    "cajoneras",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("cod_men", sqlalchemy.Integer),
    sqlalchemy.Column("fecha", sqlalchemy.DateTime),
    sqlalchemy.Column("actualizado_por", sqlalchemy.String),
    sqlalchemy.Column("envio_whatsApp", sqlalchemy.Boolean),
)

historial_transacciones_table = sqlalchemy.Table(
    "historial_transacciones",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("estado_envio", sqlalchemy.String),
    sqlalchemy.Column("fecha_actualizacion", sqlalchemy.DateTime),
    sqlalchemy.Column("actualizado_por", sqlalchemy.String),
)

comentario_table = sqlalchemy.Table(
    "comentarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("comentario", sqlalchemy.String),
    sqlalchemy.Column("fecha", sqlalchemy.DateTime),
    sqlalchemy.Column("actualizado_por", sqlalchemy.String),
)

estado_envio_table = sqlalchemy.Table(
    "estado_envio",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("estado", sqlalchemy.String),
    sqlalchemy.Column("fecha", sqlalchemy.DateTime),
    sqlalchemy.Column("actualizado_por", sqlalchemy.String),
)

estado_dinero_table = sqlalchemy.Table(
    "estado_dinero",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_bodega", sqlalchemy.Integer),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("cod_men", sqlalchemy.Integer),
    sqlalchemy.Column("estado", sqlalchemy.String),
    sqlalchemy.Column("fecha", sqlalchemy.DateTime),
    sqlalchemy.Column("actualizado_por", sqlalchemy.String),
    sqlalchemy.Column("consignatario", sqlalchemy.String),
    sqlalchemy.Column("fecha_consignacion", sqlalchemy.DateTime),
    sqlalchemy.Column("valor_consignacion", sqlalchemy.Float),
    sqlalchemy.Column("tipo_de_pago", sqlalchemy.String),
    sqlalchemy.Column("verificacion_pago", sqlalchemy.Boolean),
    sqlalchemy.Column("verificado_por", sqlalchemy.String),
    sqlalchemy.Column("numero_nequi", sqlalchemy.String),
    sqlalchemy.Column("transferido", sqlalchemy.Boolean),
    sqlalchemy.Column("banco_transferencia", sqlalchemy.String),
    sqlalchemy.Column("numero_transferencia", sqlalchemy.String),
    sqlalchemy.Column("fecha_transferencia", sqlalchemy.DateTime),
)

verificacion_dinero_table = sqlalchemy.Table(
    "verificacion_dinero",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("serial", sqlalchemy.String),
    sqlalchemy.Column("estado", sqlalchemy.String),
    sqlalchemy.Column("fecha", sqlalchemy.DateTime),
    sqlalchemy.Column("actualizado_por", sqlalchemy.String),
    sqlalchemy.Column("consignatario", sqlalchemy.String),
    sqlalchemy.Column("fecha_consignacion", sqlalchemy.DateTime),
    sqlalchemy.Column("valor_consignacion", sqlalchemy.Float),
    sqlalchemy.Column("imagen", sqlalchemy.String),
)


connect_args = {"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
engine = sqlalchemy.create_engine(config.DATABASE_URL, connect_args=connect_args)
metadata.create_all(engine)
db_args = {"min_size": 1, "max_size": 5} if "postgres" in config.DATABASE_URL else {}
database = databases.Database(config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLLBACK, **db_args)