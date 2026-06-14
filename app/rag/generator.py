from __future__ import annotations

import textwrap

from app.models.schemas import Source
from app.rag.retriever import RetrievalResult


# Creates the final answer using only retrieved documents.
class GroundedAnswerGenerator:
    # Converts search results into answer, confidence, sources, and limitations.
    def answer(self, question: str, results: list[RetrievalResult], min_score: float) -> tuple[str, str, list[Source], list[str]]:
        if not results or results[0].score < min_score:
            return (
                "I could not find a strong match in the indexed Stack Overflow Python answers. "
                "Try adding the library name, error message, or a short code snippet.",
                "low",
                [],
                ["No retrieved source crossed the configured confidence threshold."],
            )

        sources = [_to_source(result) for result in results]
        confidence = _confidence(results[0].score)
        answer_parts = [
            _lead_sentence(question, results[0]),
            _supporting_details(results[:3]),
            "Use the cited sources as grounding; behavior can still vary by Python version and library version.",
        ]
        limitations = []
        if len(results) == 1 or results[0].score - results[-1].score > 0.45:
            limitations.append("The answer is mainly grounded in one highly ranked source.")
        return (" ".join(part for part in answer_parts if part), confidence, sources, limitations)


# Starts the answer using the best matching source.
def _lead_sentence(question: str, top_result: RetrievalResult) -> str:
    answer = _first_sentences(top_result.document.answer, max_sentences=2)
    return (
        f"Based on the closest Stack Overflow match, the practical answer is: {answer}"
    )


# Adds short support from the top retrieved sources.
def _supporting_details(results: list[RetrievalResult]) -> str:
    details = []
    for index, result in enumerate(results, start=1):
        snippet = _first_sentences(result.document.answer, max_sentences=1)
        details.append(f"[{index}] {snippet}")
    return " ".join(details)


# Converts an internal result into an API source object.
def _to_source(result: RetrievalResult) -> Source:
    return Source(
        id=result.document.id,
        title=result.document.title,
        score=result.score,
        tags=result.document.tags,
        snippet=textwrap.shorten(result.document.display_text, width=360, placeholder="..."),
        source_url=result.document.source_url,
    )


# Keeps answer snippets short and readable.
def _first_sentences(text: str, max_sentences: int) -> str:
    pieces = [piece.strip() for piece in text.replace("\n", " ").split(".") if piece.strip()]
    if not pieces:
        return textwrap.shorten(text, width=260, placeholder="...")
    selected = ". ".join(pieces[:max_sentences])
    if selected and selected[-1] not in ".!?":
        selected += "."
    return textwrap.shorten(selected, width=420, placeholder="...")


# Converts numeric retrieval score into low/medium/high confidence.
def _confidence(score: float) -> str:
    if score >= 0.55:
        return "high"
    if score >= 0.25:
        return "medium"
    return "low"
