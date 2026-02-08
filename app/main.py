from fastapi import FastAPI

from app.routers import categories


app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="1.0",
    description="Учебный проект"
)

app.include_router(categories.router)


@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}
