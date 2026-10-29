import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine

from core.config import settings

# Prefer an explicit connection URL when supplied, otherwise use the
# individual DB_* settings. Escape credentials so special characters work.
DATABASE_URL = (settings.DATABASE_URL or os.getenv("DATABASE_URL") or "").strip() or (
    f"postgresql+psycopg2://{quote_plus(settings.db_user)}:"
    f"{quote_plus(settings.db_password)}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
)

