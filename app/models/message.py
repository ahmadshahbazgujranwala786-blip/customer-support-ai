from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )

    sender_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    message_type: Mapped[str] = mapped_column(
        String(20),
        default="text",
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    channel_message_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    attachments: Mapped[str] = mapped_column(
        Text,
        default="[]"
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )