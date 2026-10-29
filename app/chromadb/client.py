import chromadb

from core.config import PROJECT_ROOT

chroma_client = chromadb.PersistentClient(
    path=str(PROJECT_ROOT / "chroma_db")
)