from app.rag.documents import Document
from app.rag.ingestion import load_documents


# Repository only handles loading and caching documents.
class DocumentRepository:
    def __init__(self, dataset_path: str, max_documents: int) -> None:
        self._dataset_path = dataset_path
        self._max_documents = max_documents
        self._documents: list[Document] | None = None

    # Loads documents once, then reuses them for future requests.
    def list_documents(self) -> list[Document]:
        if self._documents is None:
            self._documents = load_documents(self._dataset_path, self._max_documents)
        return self._documents
