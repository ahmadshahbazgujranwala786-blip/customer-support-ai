from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.customer import Customer
from app.database.base import Base


class Order(Base):

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String,
        default="pending"
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0
    )

    shipping_address: Mapped[str | None] = mapped_column(Text)

    payment_method: Mapped[str | None] = mapped_column(String)

    payment_status: Mapped[str] = mapped_column(
        String,
        default="pending"
    )

    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime]

    updated_at: Mapped[datetime]

    customer: Mapped["Customer"] = relationship(
        back_populates="orders"
    )

    items = relationship(
        "OrderItem",
        back_populates="order"
    )