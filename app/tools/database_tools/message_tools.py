from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.memory.memory_tools import save_message_memory

def save_message(
    db: Session,
    conversation_id: int,
    sender_type: str,
    content: str,
    message_type: str = "text",
    channel_message_id: str | None = None,
    attachments: str = "[]",
    metadata_json: str = "{}"
):
    message = Message(
        conversation_id=conversation_id,
        sender_type=sender_type,
        message_type=message_type,
        content=content,
        channel_message_id=channel_message_id,
        attachments=attachments,
        metadata_json=metadata_json
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    conversation = db.query(Conversation).filter(
    Conversation.id == conversation_id
    ).first()
    customer_id = conversation.customer_id

    save_message_memory(
        customer_id= customer_id,
        message_id=message.id,
        conversation_id=conversation_id,
        content=content
    )
    return message

def get_conversation_messages(
    db: Session,
    conversation_id: int
):
    messages = (
    db.query(Message)
    .filter(
        Message.conversation_id == conversation_id
    )
    .order_by(Message.created_at.asc())
    .all()
)

    return messages