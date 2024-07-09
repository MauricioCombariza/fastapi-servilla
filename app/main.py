import logging
from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import database
from app.logging_conf import configure_logging
from app.routers.order import router as order_router
from app.routers.user import router as user_router
from app.routers.process import router as process_router
from app.routers.chat import router as chat_router
from app.routers.money import router as money_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Configuring database connection")
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:3000",
    "https://servilla.com.co",   # Permitir solicitudes desde este origen
]



# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow credentials if needed
    allow_methods=["*"],  # Allow all methods (customize if needed)
    allow_headers=["*"],  # Allow all headers (customize if needed)
)

app.add_middleware(CorrelationIdMiddleware)
app.include_router(order_router)
app.include_router(user_router)
app.include_router(process_router)
app.include_router(chat_router)
app.include_router(money_router)



@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)