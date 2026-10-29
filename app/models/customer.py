from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
import uuid

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4())
    )

    sender_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default= None
    )

    conversations = relationship(
        "Conversation",
        back_populates="customer"
    )

    orders = relationship("Order", back_populates="customer")