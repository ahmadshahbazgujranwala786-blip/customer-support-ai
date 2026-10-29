from app.database.database import engine
from app.database.base import Base

# Models import karna zaroori hai
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.product import Product
from app.models.service import Service
def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
