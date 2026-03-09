from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        CheckConstraint('grade >= 1 AND grade <= 5', name='check_grade_range'), # Проверка заданной оценки (1;5)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    comment: Mapped[str] = mapped_column(Text)
    comment_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    change_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product: Mapped['Product'] = relationship('Product', back_populates='reviews')
    user: Mapped['User'] = relationship('User', back_populates='reviews')