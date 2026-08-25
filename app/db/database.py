from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from app.core.config import settings


engine = create_engine(settings.DB_URL)

Base = declarative_base()

LocalSession = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind = engine
)

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()