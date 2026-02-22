from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_db


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).join(CategoryModel).where(ProductModel.is_active == True,
                                                          CategoryModel.is_active == True)
    db_products = db.scalars(stmt).all()
    return db_products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый товар.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                    CategoryModel.is_active == True)
    if db.scalars(stmt).first() is None:
        raise HTTPException(status_code=404, detail=f"Category with id {product.category_id} not found")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    if db.scalars(stmt).first() is None:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found or inactive")

    stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                      ProductModel.is_active == True)
    db_products = db.scalars(stmt).all()
    return db_products


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    p_stmt = select(ProductModel).where(ProductModel.id == product_id,
                                        ProductModel.is_active == True)
    db_product = db.scalars(p_stmt).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found or inactive")

    c_stmt = select(CategoryModel).where(CategoryModel.id == db_product.category_id,
                                         CategoryModel.is_active == True)
    if db.scalars(c_stmt).first() is None:
        raise HTTPException(status_code=400, detail=f"Category for product {product_id} not found or inactive")

    return db_product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """
    Обновляет товар по его ID.
    """
    p_stmt = select(ProductModel).where(ProductModel.id == product_id,
                                        ProductModel.is_active == True)
    db_product = db.scalars(p_stmt).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found or inactive")

    c_stmt = select(CategoryModel).where(CategoryModel.id == db_product.category_id,
                                         CategoryModel.is_active == True)
    if db.scalars(c_stmt).first() is None:
        raise HTTPException(status_code=400, detail=f"Category for product {product_id} not found or inactive")

    db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    if db.scalars(stmt).first() is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found or inactive")

    db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    db.commit()
    return {"status": "success", "message": "Product marked as inactive"}