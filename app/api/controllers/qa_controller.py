from functools import lru_cache

from app.models.schemas import AskRequest, AskResponse, HealthResponse
from app.services.qa_service import QAService, get_qa_service


# Controller keeps HTTP/API handling separate from the RAG logic.
class QAController:
    def __init__(self, service: QAService) -> None:
        self._service = service

    # Returns app status and indexed document count.
    def health(self) -> HealthResponse:
        stats = self._service.stats()
        return HealthResponse(status="ok", document_count=stats["document_count"])

    # Sends the user question to the QA service.
    def ask(self, request: AskRequest) -> AskResponse:
        return self._service.answer(request)


# Creates one controller object and reuses it.
@lru_cache
def get_qa_controller() -> QAController:
    return QAController(get_qa_service())
