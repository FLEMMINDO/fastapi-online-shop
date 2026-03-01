from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import categories, products, users, reviews, cart, orders


app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="1.0",
    description="Учебный проект"
)

app.mount('/media', StaticFiles(directory='media'), name='media')

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(orders.router)

@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}
