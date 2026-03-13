from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse
from app.config import settings

_url = urlparse(settings.DATABASE_URL)
_password = settings.DB_PASSWORD if settings.DB_PASSWORD else _url.password

engine = create_engine(
    URL.create(
        drivername="postgresql",
        username=_url.username,
        password=_password,
        host=_url.hostname,
        port=_url.port,
        database=_url.path.lstrip("/"),
        query={"sslmode": "require"},
    ),
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def test_connection() -> bool:
    """Teste la connexion à la base de données. Retourne True si OK."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False