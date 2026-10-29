from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message

def get_or_create_conversation(
    db: Session,
    customer_id: int,
    channel : str
):

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.customer_id == customer_id,
            Conversation.status == "active"
        )
        .first()
    )

    if conversation:
        
        return conversation

    conversation = Conversation(
        customer_id=customer_id,
        status="active",
        channel = channel
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

