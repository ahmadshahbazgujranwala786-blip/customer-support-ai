
from app.chromadb.BaseEmbeddingMigrator import BaseEmbeddingMigrator
from app.database.session import SessionLocal
from app.models.service import Service

class ServiceEmbeddingMigrator(
    BaseEmbeddingMigrator
):

    def fetch_data(self):

        return self.db.query(Service).all()


    def create_document(self, service):

        return f"""
        Service:
        {service.name}

        Description:
        {service.description}

        Ideal For:
        {service.ideal_for}
        """


    def create_metadata(self, service):

        return {
            "name": service.name,
            "category": service.category,
            "price": service.price_display
        }