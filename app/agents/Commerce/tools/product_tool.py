import chromadb
import psycopg2
from psycopg2.extras import RealDictCursor
import tensorflow_hub as hub
from langchain_core.tools import tool
from core.config import settings, PROJECT_ROOT

# ==============================
# TensorFlow Embedding Function
# ==============================

class TensorflowEmbeddingFunction:

    def __init__(self):
        # Load the large model only when product search actually needs it.
        # Importing the support API should not download or initialize TensorFlow Hub.
        self.model = None

    def _get_model(self):
        if self.model is None:
            self.model = hub.load(
                "https://tfhub.dev/google/universal-sentence-encoder/4"
            )
        return self.model

    def embed_documents(self, input):
        embeddings = self._get_model()(input)
        return embeddings.numpy().tolist()


    def embed_query(self, input):
        embeddings = self._get_model()(input)
        return embeddings.numpy().tolist()
    
    def __call__(self, input):
        embeddings = self._get_model()(input)
        return embeddings.numpy()[0].tolist()

    def name(self):
        return "tensorflow_universal_sentence_encoder"



# ==============================
# ChromaDB Setup
# ==============================

client = chromadb.PersistentClient(
    path=str(PROJECT_ROOT / "chroma_db")
)


embedding_function = TensorflowEmbeddingFunction()


collection = client.get_collection(
    name="product_embeddings",
    embedding_function=embedding_function
)



# ==============================
# PostgreSQL Connection
# ==============================

def get_db_connection():

    return psycopg2.connect(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )



# ==============================
# Search Products Tool
# ==============================
@tool
def search_products(
    query: str,
    limit: int = 5,
    similarity_threshold: float = 0.45,
):
    """
    Search products using semantic search + PostgreSQL filtering.

    Args:
        query: Product name, brand, category or keyword.
        limit: Maximum products to return.
        similarity_threshold: Maximum acceptable vector distance.

    Returns:
        List of matching products ordered by semantic relevance.
    """

    print("\n🔎 PRODUCT SEARCH")
    print(f"Query: {query}")

    results = collection.query(
        query_texts=[query],
        n_results=limit * 3
    )

    ids = results["ids"][0]
    ids = [
    int(pid.replace("product_", ""))
    for pid in ids
    ]  

    if not ids:
        return []

    conn = get_db_connection()

    cur = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cur.execute(
        """
        SELECT
            id,
            name,
            description,
            category,
            price,
            metadata,
            status

        FROM product

        WHERE
            id = ANY(%s)
            AND status='active'
        """,
        (ids,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # -----------------------------
    # Step 4 : Preserve Ranking
    # -----------------------------

    ranking = {
        product_id: index
        for index, product_id in enumerate(ids)
    }

    rows.sort(
        key=lambda x: ranking[x["id"]]
    )

    # -----------------------------
    # Step 5 : Apply Final Limit
    # -----------------------------

    return rows[:limit]