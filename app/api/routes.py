# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends

from app.api.controllers.qa_controller import QAController, get_qa_controller
from app.models.schemas import AskRequest, AskResponse, HealthResponse

router = APIRouter()


# Health endpoint: checks if the API is running.
@router.get("/health", response_model=HealthResponse)
def health(controller: QAController = Depends(get_qa_controller)) -> HealthResponse:
    return controller.health()


# Ask endpoint: receives a question and returns a grounded answer.
@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    controller: QAController = Depends(get_qa_controller),
) -> AskResponse:
    return controller.ask(request)
