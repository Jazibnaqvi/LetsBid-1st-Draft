import chromadb
from chromadb.api import ClientAPI

from app.core.config import settings


class ChromaClient:
    def __init__(self) -> None:
        self._client: ClientAPI | None = None

    def initialize(self) -> None:
        settings.chroma_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(settings.chroma_path))

    @property
    def client(self) -> ClientAPI:
        if self._client is None:
            raise RuntimeError("ChromaDB client is not initialized.")
        return self._client

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    def close(self) -> None:
        self._client = None


chroma_client = ChromaClient()
