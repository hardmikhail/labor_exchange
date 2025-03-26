from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sqlalchemy.client import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор вакансии")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="Идентификатор пользователя"
    )
    title: Mapped[str] = mapped_column(comment="Название вакансии")
    description: Mapped[str] = mapped_column(comment="Описание вакансии")
    salary_from: Mapped[Decimal] = mapped_column(Numeric(10, 2), comment="Зарплата от")
    salary_to: Mapped[Decimal] = mapped_column(Numeric(10, 2), comment="Зарплата до")
    is_active: Mapped[bool] = mapped_column(comment="Активна ли вакансия")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="Дата создания записи",
    )
    user: Mapped["User"] = relationship(back_populates="jobs")  # noqa
    responses: Mapped[list["Response"]] = relationship(  # noqa
        back_populates="job", cascade="all, delete-orphan"
    )
