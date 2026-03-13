from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List

ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str
    DB_PASSWORD: str = ""

    # API
    PROJECT_NAME: str = "ObRail Europe API"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "2.0.0"

    # Sécurité
    SECRET_KEY: str = "change-me-in-production"
    API_KEY: str = "obrail-api-key-2026"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=True,
    )


settings = Settings()