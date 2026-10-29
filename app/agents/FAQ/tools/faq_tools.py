import re

import chromadb
from chromadb.utils import embedding_functions
from core.config import PROJECT_ROOT

# The knowledge collection already stores each knowledge record's text and
# metadata. Read from Chroma directly so FAQ retrieval does not depend on a
# separate PostgreSQL knowledge_base table being present.
CHROMA_PATH = str(PROJECT_ROOT / "chroma_db")
COLLECTION_NAME = "knowledge_base_embeddings"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn,
)


def _split_document(document: str) -> tuple[str, str]:
    """Extract a title/content pair from the stored knowledge document."""
    match = re.match(r"^Title:\s*(.*?)\s+Content:\s*(.*)$", document or "", re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", (document or "").strip()


def get_knowledge(query: str, top_k: int = 3) -> dict:
    """Retrieve FAQ/policy knowledge from the persistent Chroma collection."""
    try:
        print("Get knowledge tool is being used........")
        search_result = collection.query(
            query_texts=[query],
            n_results=max(1, min(int(top_k), 10)),
            include=["documents", "metadatas", "distances"],
        )

        ids = (search_result.get("ids") or [[]])[0]
        if not ids:
            return {
                "success": False,
                "knowledge": [],
                "message": "No relevant knowledge found.",
            }

        documents = (search_result.get("documents") or [[]])[0]
        metadatas = (search_result.get("metadatas") or [[]])[0]
        distances = (search_result.get("distances") or [[]])[0]

        knowledge = []
        for index, chroma_id in enumerate(ids):
            metadata = (metadatas[index] if index < len(metadatas) else None) or {}
            status = str(metadata.get("status", "active")).lower()
            if status != "active":
                continue

            document = documents[index] if index < len(documents) else ""
            title, content = _split_document(document or "")
            raw_id = metadata.get("db_id", chroma_id)
            if isinstance(raw_id, str) and raw_id.startswith("kb_"):
                raw_id = raw_id[3:]

            try:
                record_id = int(raw_id)
            except (TypeError, ValueError):
                record_id = str(chroma_id)

            distance = distances[index] if index < len(distances) else None
            similarity = round(1 - float(distance), 3) if distance is not None else None

            knowledge.append({
                "id": record_id,
                "type": metadata.get("type", "faq"),
                "title": title or str(chroma_id),
                "content": content,
                "category": metadata.get("category", "general"),
                "metadata": metadata,
                "similarity_score": similarity,
            })

        if not knowledge:
            return {
                "success": False,
                "knowledge": [],
                "message": "No active knowledge records found.",
            }

        return {
            "success": True,
            "knowledge": knowledge,
            "total_results": len(knowledge),
        }
    except Exception as exc:
        print(f"Knowledge retrieval failed: {type(exc).__name__}: {exc}")
        return {
            "success": False,
            "knowledge": [],
            "error": str(exc),
        }
