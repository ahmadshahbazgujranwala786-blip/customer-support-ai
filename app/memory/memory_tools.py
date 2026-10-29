from app.memory.chroma_client import message_collection
from app.memory.embedding_service import create_embedding


def save_message_memory(
    message_id: int,
    customer_id: int,
    conversation_id: int,
    content: str
):

    embedding = create_embedding(content)


    message_collection.add(
        ids=[
            str(message_id)
        ],

        embeddings=[
            embedding
        ],

        documents=[
            content
        ],

        metadatas=[
            {
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "message_id": message_id
            }
        ]
    )