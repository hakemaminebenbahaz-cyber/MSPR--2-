from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI pour obtenir une session DB. Fermée automatiquement après usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
