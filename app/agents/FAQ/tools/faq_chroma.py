import chromadb
from chromadb.utils import embedding_functions
import psycopg2
from psycopg2.extras import RealDictCursor
import json # to parse metadata if it's JSONB
from core.config import settings, PROJECT_ROOT

# Config
CHROMA_PATH = str(PROJECT_ROOT / "chroma_db")
COLLECTION_NAME = "knowledge_base_embeddings" # or faq_knowledge, let's keep it generic

# Connect PostgreSQL
conn = psycopg2.connect(
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Fetch only active records
cur.execute("""
    SELECT id, type, title, content, category, metadata, status 
    FROM knowledge_base 
    WHERE status = 'active'
""")
rows = cur.fetchall()

# Chroma setup
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Delete existing collection if any, or get/create. I'll use get_or_create.
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)

# Prepare batches (Chroma can handle bulk add)
ids = []
documents = []
metadatas = []

for row in rows:
    # Document = Title + Content (best for semantic search)
    doc_text = f"Title: {row['title']}\nContent: {row['content']}"
    
    # Metadata: flatten useful fields
    meta = {
        "db_id": row['id'],
        "type": row['type'],
        "category": row['category'] or "general",
        "status": row['status']
    }
    # If there's extra metadata JSON, merge it carefully (limit size if needed)
    if row['metadata']:
        try:
            extra = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
            if isinstance(extra, dict):
                # Add only simple types to avoid ChromaDB serialization errors
                for k, v in extra.items():
                    if isinstance(v, (str, int, float, bool)):
                        meta[f"meta_{k}"] = v
        except:
            pass
    
    ids.append(f"kb_{row['id']}")
    documents.append(doc_text)
    metadatas.append(meta)

# Add to ChromaDB in batches (to avoid memory issues if huge)
batch_size = 100
for i in range(0, len(ids), batch_size):
    collection.add(
        ids=ids[i:i+batch_size],
        documents=documents[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size]
    )
    print(f"✅ Added batch {i//batch_size + 1}")

cur.close()
conn.close()
print("🎉 Knowledge Base migration complete!")