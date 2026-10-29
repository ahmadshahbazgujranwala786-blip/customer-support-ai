from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database.base import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    price_display: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    ideal_for: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    availability: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="available"
    )

    condition: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="new"
    )

    brand: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="AgenticFlow AI"
    )

    link: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return (
            f"<Service(id={self.id}, "
            f"name='{self.name}', "
            f"category='{self.category}')>"
        )