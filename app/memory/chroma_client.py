import chromadb

from core.config import PROJECT_ROOT


client = chromadb.PersistentClient(
    path=str(PROJECT_ROOT / "chroma_db")
)


message_collection = client.get_or_create_collection(
    name="customer_messages"
)