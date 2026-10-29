from langchain_core.tools import tool

from app.chromadb.client import chroma_client

service_collection = chroma_client.get_collection(
    name="service_embeddings"
)

@tool
def search_services(query: str):
    """
    Search available company services using semantic search.

    Use this tool when customer asks about:
    - services
    - automation solutions
    - available solutions
    - company offerings
    - service details
    """

    try:

        print("🔎 SERVICE SEARCH")
        print("Query:", query)


        results = service_collection.query(
            query_texts=[query],
            n_results=5
        )


        services = []


        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]


        for doc, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            services.append(
                {
                    "service_id": metadata.get("service_id"),
                    "name": metadata.get("name"),
                    "category": metadata.get("category"),
                    "price_display": metadata.get("price_display"),
                    "availability": metadata.get("availability"),
                    "description": doc,
                    "similarity_score": distance
                }
            )


        print("SERVICE RESULT:")
        print(services)


        return services


    except Exception as e:

        print(
            f"❌ Service search error: {str(e)}"
        )

        return []