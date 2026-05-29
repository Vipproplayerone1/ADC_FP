from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Personalized Learning Assistant"
    app_env: str = "development"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    vector_store: str = "chroma"
    chroma_persist_dir: str = "vector_db/chroma"
    chroma_collection: str = "pla_chunks"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LLM: a local Ollama daemon speaking the OpenAI-compatible chat API.
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434/v1"

    @property
    def active_llm_key(self) -> str:
        # Ollama ignores the key, but the OpenAI SDK requires a non-empty string.
        return "ollama"

    @property
    def active_llm_model(self) -> str:
        return self.ollama_model

    @property
    def active_llm_base_url(self) -> str:
        return self.ollama_base_url

    top_k: int = Field(default=5, ge=1, le=50)
    chunk_size: int = Field(default=800, ge=100, le=4000)
    chunk_overlap: int = Field(default=150, ge=0, le=1000)

    upload_dir: str = "data/raw/uploaded_pdfs"
    max_upload_size_mb: int = 50

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def chroma_path(self) -> Path:
        return (self.project_root / self.chroma_persist_dir).resolve()

    @property
    def upload_path(self) -> Path:
        return (self.project_root / self.upload_dir).resolve()

    @property
    def prompts_dir(self) -> Path:
        return Path(__file__).resolve().parent / "prompts"


@lru_cache
def get_settings() -> Settings:
    return Settings()
