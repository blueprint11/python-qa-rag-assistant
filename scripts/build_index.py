import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.repositories.document_repository import DocumentRepository
from app.rag.retriever import KeywordRetriever


def main() -> None:
    dataset_path = os.getenv("DATASET_PATH", "data/sample_python_qa.csv")
    max_documents = int(os.getenv("MAX_DOCUMENTS", "5000"))
    repository = DocumentRepository(dataset_path, max_documents)
    documents = repository.list_documents()
    retriever = KeywordRetriever(documents)
    print(f"Indexed {retriever.document_count} documents from {dataset_path}")


if __name__ == "__main__":
    main()
