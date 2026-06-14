# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


# Request body for POST /ask.
class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=8)


# One source document used to support the answer.
class Source(BaseModel):
    id: str
    title: str
    score: float
    tags: list[str] = []
    snippet: str
    source_url: str | None = None


# Response body returned by POST /ask.
class AskResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    sources: list[Source]
    limitations: list[str] = []


# Response body returned by GET /health.
class HealthResponse(BaseModel):
    status: str
    document_count: int
