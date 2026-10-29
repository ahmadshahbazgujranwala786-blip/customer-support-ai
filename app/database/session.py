from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.database import engine


# Use the same engine as the rest of the application. The previous version
# created a second engine with hard-coded local credentials, which could make
# API requests connect to a different database from the rest of the app.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()