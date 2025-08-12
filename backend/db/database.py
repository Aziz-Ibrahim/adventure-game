from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core.config import settings


engine = create_engine(
    settings.DATABASE_UR
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """
    Provides a database session for use in the application.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Creates all tables in the database.
    """
    Base.metadata.create_all(bind=engine)