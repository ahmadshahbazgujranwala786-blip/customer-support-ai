from sqlalchemy.orm import Session
from app.memory.chroma_client import message_collection
from app.memory.embedding_service import create_embedding
from app.models.message import Message

def retrieve_memory(
    db: Session,
    customer_id: int,
    query: str,
    limit: int = 5
):
    query_embedding = create_embedding(query)
    results = message_collection.query(
        query_embeddings=[query_embedding],
        n_results= limit,
        where= { 
            "customer_id" : customer_id
        }

    )
        # 3. Extract message IDs
    message_ids = results["ids"][0]


    if not message_ids:
        return []


    # ChromaDB IDs are strings
    message_ids = [
        int(id)
        for id in message_ids
    ]


    # 4. Fetch actual messages from PostgreSQL
    messages = (
        db.query(Message)
        .filter(
            Message.id.in_(message_ids)
        )
        .all()
    )


    return messages
