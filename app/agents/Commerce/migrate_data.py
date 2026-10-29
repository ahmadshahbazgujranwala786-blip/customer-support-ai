import psycopg2
from psycopg2.extras import RealDictCursor

import chromadb
import tensorflow_hub as hub
from core.config import settings, PROJECT_ROOT


# -----------------------------
# TensorFlow Embedding Function
# -----------------------------

class TensorflowEmbeddingFunction:

    def __init__(self):
        self.model = hub.load(
            "https://tfhub.dev/google/universal-sentence-encoder/4"
        )

    def __call__(self, input):
        embeddings = self.model(input)
        return embeddings.numpy().tolist()

    def name(self):
        return "tensorflow_universal_sentence_encoder"


# -----------------------------
# PostgreSQL Connection
# -----------------------------

conn = psycopg2.connect(
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
)

cur = conn.cursor(
    cursor_factory=RealDictCursor
)


cur.execute("""
    SELECT 
        id,
        name,
        description,
        category,
        price,
        metadata,
        status
    FROM product
    WHERE status = 'active'
""")

products = cur.fetchall()


print(f"Products found: {len(products)}")


# -----------------------------
# ChromaDB Setup
# -----------------------------

client = chromadb.PersistentClient(
    path=str(PROJECT_ROOT / "chroma_db")
)


embedding_function = TensorflowEmbeddingFunction()


collection = client.get_or_create_collection(
    name="product_embeddings",
    embedding_function=embedding_function
)


# -----------------------------
# Prepare Data
# -----------------------------

ids = []
documents = []
metadatas = []


for product in products:

    document = f"""
    Product Name: {product['name']}
    
    Description:
    {product['description']}
    
    Category:
    {product['category']}
    """


    metadata = {
        "db_id": product["id"],
        "category": product["category"],
        "price": float(product["price"]),
        "status": product["status"]
    }


    ids.append(
        f"product_{product['id']}"
    )

    documents.append(document)

    metadatas.append(metadata)

collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print("✅ Products migrated successfully")

cur.close()
conn.close()