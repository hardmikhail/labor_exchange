from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sqlalchemy.client import Base


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="user_id_job_id_uc"),)

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор записи")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="Идентификатор пользователя"
    )
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), comment="Идентификатор вакансии")
    message: Mapped[Optional[str]] = mapped_column(
        nullable=True, default=None, comment="Сопроводительное письмо"
    )
    user: Mapped["User"] = relationship(back_populates="responses")  # noqa
    job: Mapped["Job"] = relationship(back_populates="responses")  # noqa
