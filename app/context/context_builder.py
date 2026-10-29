from app.models.customer import Customer
from app.models.message import Message


def serialize_message(message: Message) -> dict:
    """
    Convert SQLAlchemy Message object into a standard dictionary.
    """

    return {
        "id": message.id,
        "role": message.sender_type,
        "type": message.message_type,
        "content": message.content,
        "created_at": message.created_at.isoformat()
    }


def build_context(
    customer: Customer,
    current_message: Message,
    current_conversation: list[Message],
    relevant_memories: list[Message],
) -> dict:
    """
    Build a standardized context object for downstream components.
    """

    return {

        "customer": {
            "id": customer.id,
            "user_id": customer.user_id,
            "name": customer.sender_name,
            "channel": customer.channel,
        },

        "current_message": serialize_message(current_message),

        "current_conversation": [
            serialize_message(message)
            for message in current_conversation
        ],

        "relevant_memories": [
            serialize_message(message)
            for message in relevant_memories
        ],
    }

