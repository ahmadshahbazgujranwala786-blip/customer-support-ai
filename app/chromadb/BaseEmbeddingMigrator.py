import chromadb

from core.config import PROJECT_ROOT
class BaseEmbeddingMigrator:

    def __init__(
        self,
        db,
        collection_name
    ):
        self.db = db
        self.collection_name = collection_name
    def chroma_client(self):
        return chromadb.PersistentClient(
            path=str(PROJECT_ROOT / "chroma_db")
        )

    def fetch_data(self):
        raise NotImplementedError


    def create_document(self, item):
        raise NotImplementedError

    def get_collection(self):

        return self.chroma_client().get_or_create_collection(
            name=self.collection_name
        )

    def create_metadata(self, item):
        raise NotImplementedError


    def migrate(self):

        data = self.fetch_data()

        ids = []
        documents = []
        metadatas = []


        for item in data:

            ids.append(str(item.id))

            documents.append(
                self.create_document(item)
            )

            metadatas.append(
                self.create_metadata(item)
            )

        collection = self.get_collection(
            self.collection_name
        )

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )