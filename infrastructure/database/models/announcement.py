from datetime import datetime, date
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Integer, Date, BigInteger
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base, TableNameMixin

class Announcement(Base, TableNameMixin):
    """
    Модель объявления с автоматическими timestamp и связью с пользователем
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64))
    people_needed: Mapped[int] = mapped_column(Integer, nullable=False)
    route: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Автоматические временные метки
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Отношение многие-к-одному к пользователю
    user: Mapped["User"] = relationship("User", back_populates="announcements")
