# pyrefly: ignore [missing-import]
from functools import lru_cache
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


# Stores all app settings loaded from environment variables.
class Settings(BaseSettings):
    app_name: str = "Python Programming Q&A Assistant"
    environment: str = "local"
    dataset_path: str = "data/processed_python_qa_5k.csv"
    max_documents: int = 5000
    top_k: int = 4
    min_retrieval_score: float = 0.25

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Loads settings once so every file uses the same config.
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
