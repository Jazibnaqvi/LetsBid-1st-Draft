from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "LetsBid"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    sqlite_database_url: str = "sqlite:///./data/letsbid.db"
    chroma_persist_dir: str = "./data/chroma"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ner_max_input_chars: int = 120_000
    capability_csv_file: str = "./data/capability_library.csv"

    @property
    def sqlite_path(self) -> Path:
        url = self.sqlite_database_url
        if url.startswith("sqlite:///"):
            relative = url.replace("sqlite:///", "", 1)
            return (BACKEND_ROOT / relative).resolve()
        return BACKEND_ROOT / "data" / "letsbid.db"

    @property
    def chroma_path(self) -> Path:
        return (BACKEND_ROOT / self.chroma_persist_dir).resolve()

    @property
    def capability_csv_path(self) -> Path:
        return (BACKEND_ROOT / self.capability_csv_file).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
