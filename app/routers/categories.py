from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_async_db
from app.auth import get_current_admin


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных категорий.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    categories = (await db.scalars(stmt)).all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_admin)):
    """
    Создаёт новую категорию.
    """
    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                           CategoryModel.is_active == True)
        parent = (await db.scalars(stmt)).first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    # Создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    return db_category


@router.put("/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def update_category(category_id: int, category: CategoryCreate, db: AsyncSession = Depends(get_async_db),\
                          current_user: UserModel = Depends(get_current_admin)):
    """
    Обновляет категорию по её ID.
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    db_category = (await db.scalars(stmt)).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                                  CategoryModel.is_active == True)
        parent = (await db.scalars(parent_stmt)).first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
        if parent.id == category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category cannot be its own parent")

    # Обновление категории
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump(exclude_unset=True))
    )
    await db.commit()
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_admin)):
    """
    Логически удаляет категорию по её ID, устанавливая is_active=False.
    """
    # Проверка существования активной категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    category = (await db.scalars(stmt)).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Логическое удаление категории (установка is_active=False)
    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False))
    await db.commit()

    return {"status": "success", "message": "Category marked as inactive"}