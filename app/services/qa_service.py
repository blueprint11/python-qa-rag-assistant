from functools import lru_cache

from app.core.config import settings
from app.models.schemas import AskRequest, AskResponse
from app.rag.generator import GroundedAnswerGenerator
from app.rag.retriever import KeywordRetriever
from app.repositories.document_repository import DocumentRepository


# Service contains the main RAG flow: retrieve first, then answer.
class QAService:
    def __init__(
        self,
        repository: DocumentRepository,
        retriever: KeywordRetriever,
        generator: GroundedAnswerGenerator,
    ) -> None:
        self._repository = repository
        self._retriever = retriever
        self._generator = generator

    # Returns simple stats for the health endpoint.
    def stats(self) -> dict[str, int]:
        return {"document_count": self._retriever.document_count}

    # Main function that answers a user question.
    def answer(self, request: AskRequest) -> AskResponse:
        top_k = request.top_k or settings.top_k
        results = self._retriever.retrieve(request.question, top_k=top_k)
        answer, confidence, sources, limitations = self._generator.answer(
            question=request.question,
            results=results,
            min_score=settings.min_retrieval_score,
        )
        return AskResponse(
            question=request.question,
            answer=answer,
            confidence=confidence,
            sources=sources,
            limitations=limitations,
        )


# Builds the repository, retriever, and generator once.
@lru_cache
def get_qa_service() -> QAService:
    repository = DocumentRepository(settings.dataset_path, settings.max_documents)
    documents = repository.list_documents()
    retriever = KeywordRetriever(documents)
    generator = GroundedAnswerGenerator()
    return QAService(repository, retriever, generator)
