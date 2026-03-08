from pathlib import Path
from uuid import uuid4
from loguru import logger
from celery import Celery
from app.c_tasks import call_background_task
from app.config import CELERY_BROKER, CELERY_BACKEND
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.routers import categories, products, users, reviews, cart, orders, payments

LOGGER_PATH = '/var/logs'
logger.add(f"{LOGGER_PATH}/info.log",
           format="{time:YYYY-MM-DD HH:mm:ss} - {extra[log_id]} - {level} - {message}",
           level="INFO", enqueue=True, colorize=True)  # rotation='00:00' compression='gz' retention='2 month'


origins = [
    '*'  # Заменить на домен
]

app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="1.0",
    description="Учебный проект"
)


celery = Celery(
    __name__,
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    broker_connection_retry_on_startup=True
)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info('Successfully accessed ' + request.url.path)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Заменить на домен
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(HTTPSRedirectMiddleware) #  UnCOMMENT

app.mount('/media', StaticFiles(directory='media'), name='media')

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)


@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    name = 'kek'
    call_background_task.delay(name)
    return {"message": "Добро пожаловать в API интернет-магазина!"}
