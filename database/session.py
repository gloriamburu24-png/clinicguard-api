from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    """Create and return the database engine lazily."""
    if DATABASE_URL:
        return create_engine(DATABASE_URL, echo=True)
    else:
        # Fallback to SQLite for testing
        return create_engine("sqlite:///./test.db", echo=True, connect_args={"check_same_thread": False})

# Lazy engine - created only when needed
_engine = None

def get_engine_singleton():
    """Get or create the engine singleton."""
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine

def get_session():
    with Session(get_engine_singleton()) as session:
        yield session

def create_tables():
    SQLModel.metadata.create_all(get_engine_singleton())