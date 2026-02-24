from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.db_depends import get_async_db
from app.auth import get_current_user, get_current_buyer

from datetime import datetime


router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()

@router.get('/', response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    GET Получение всех отзывов
    """
    reviews_q = select(ReviewModel).where(ReviewModel.is_active == True)
    db_reviews = (await db.scalars(reviews_q)).all()

    return db_reviews


@router.get('/products/{product_id}', response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_reviews_by_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    GET Получение всех отзывов по товару product_id
    """
    reviews_q = select(ReviewModel).where(ReviewModel.product_id == product_id, ReviewModel.is_active == True)
    db_reviews = (await db.scalars(reviews_q)).all()

    return db_reviews


@router.post('/', response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_buyer)):
    """
    POST Создание отзыва о товаре
    """
    product_q = select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    db_product = (await db.scalars(product_q)).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f'Product with id {review.product_id} not found or inactive')

    review_q = select(ReviewModel).where(ReviewModel.product_id == review.product_id,
                                         ReviewModel.user_id == current_user.id,
                                         ReviewModel.is_active == True)

    if (await db.scalars(review_q)).first():
        raise HTTPException(status_code=409, detail=f'You already left review for product {review.product_id}')

    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    await update_product_rating(db, db_review.product_id)

    return db_review


@router.put('/{review_id}', response_model=ReviewSchema, status_code=status.HTTP_200_OK)
async def update_review(review_id: int, review: ReviewCreate, db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_buyer)):
    """
    PUT Обновление отзыва по review_id
    """
    review_q = select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    db_review = (await db.scalars(review_q)).first()
    if not db_review:
        raise HTTPException(status_code=404, detail=f'Product with id {review_id} not found or inactive')
    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=f'No rights to change review {review_id}')

    await db.execute(
        update(ReviewModel)
        .where(ReviewModel.id == review_id)
        .values(**review.model_dump(exclude_unset=True), change_time=datetime.now())
    )
    await db.commit()
    await db.refresh(db_review)
    await update_product_rating(db, db_review.product_id)

    return db_review


@router.delete('/{review_id}', status_code=status.HTTP_200_OK)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_user)):
    """
    DELETE Удаление отзыва по review_id
    """
    review_q = select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    db_review = (await db.scalars(review_q)).first()
    if not db_review:
        raise HTTPException(status_code=404, detail=f'Product with id {review_id} not found or inactive')
    if not (db_review.user_id == current_user.id and current_user.role == 'buyer') and not current_user.role == 'admin':
        raise HTTPException(status_code=403, detail=f'No rights to delete review {review_id}')

    db_review.is_active = False
    await db.commit()
    await update_product_rating(db, db_review.product_id)

    return {"status": "success", "message": "Review deleted"}
