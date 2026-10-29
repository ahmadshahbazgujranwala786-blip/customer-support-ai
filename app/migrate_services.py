from sqlalchemy.orm import Session

from chromadb import PersistentClient
from core.config import PROJECT_ROOT
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.database.session import SessionLocal
from app.models.service import Service

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = PersistentClient(path=str(PROJECT_ROOT / "chroma_db"))

service_collection = client.get_or_create_collection(
    name="service_embeddings",
    embedding_function=embedding_function
)


db: Session = SessionLocal()

services = db.query(Service).all()

print(f"Found {len(services)} services.")

ids = []
documents = []
metadatas = []

for service in services:

    ids.append(str(service.id))

    documents.append(
        f"""
Service Name:
{service.name}

Category:
{service.category}

Description:
{service.description}

Ideal For:
{service.ideal_for}

Price:
{service.price_display}

Availability:
{service.availability}

Brand:
{service.brand}
""".strip()
    )

    metadatas.append(
        {
            "service_id": service.id,
            "name": service.name,
            "slug": service.slug,
            "category": service.category,
            "price_display": service.price_display,
            "ideal_for": service.ideal_for,
            "availability": service.availability,
            "condition": service.condition,
            "brand": service.brand,
            "link": service.link,
        }
    )

if ids:

    service_collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"✅ Successfully migrated {len(ids)} services.")

else:

    print("⚠ No services found.")

db.close()