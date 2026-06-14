from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from app.rag.documents import Document

_TOKEN_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "python",
    "that",
    "the",
    "this",
    "to",
    "with",
}


@dataclass(frozen=True)
class RetrievalResult:
    document: Document
    score: float


# Searches documents and finds the best matches for a question.
class KeywordRetriever:
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents
        self._doc_vectors: list[Counter[str]] = []
        self._idf: dict[str, float] = {}
        self._build_index()

    # Returns how many documents were indexed.
    @property
    def document_count(self) -> int:
        return len(self._documents)

    # Searches the index and returns the top matching documents.
    def retrieve(self, query: str, top_k: int) -> list[RetrievalResult]:
        query_terms = _tokenize(query)
        if not query_terms:
            return []
        query_vector = Counter(query_terms)

        scored: list[RetrievalResult] = []
        for document, doc_vector in zip(self._documents, self._doc_vectors):
            score = self._cosine(query_vector, doc_vector)
            score += self._metadata_boost(query_terms, document)
            if score > 0:
                scored.append(RetrievalResult(document=document, score=round(score, 4)))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    # Builds a small TF-IDF style search index in memory.
    def _build_index(self) -> None:
        document_frequency: Counter[str] = Counter()
        raw_vectors: list[Counter[str]] = []

        for document in self._documents:
            terms = _tokenize(document.searchable_text)
            vector = Counter(terms)
            raw_vectors.append(vector)
            document_frequency.update(vector.keys())

        document_count = max(len(raw_vectors), 1)
        self._idf = {
            term: math.log((1 + document_count) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }

        self._doc_vectors = [
            Counter({term: count * self._idf.get(term, 1.0) for term, count in vector.items()})
            for vector in raw_vectors
        ]

    # Calculates similarity between the user question and one document.
    def _cosine(self, query_vector: Counter[str], doc_vector: Counter[str]) -> float:
        weighted_query = {
            term: count * self._idf.get(term, 1.0) for term, count in query_vector.items()
        }
        numerator = sum(weighted_query.get(term, 0.0) * doc_vector.get(term, 0.0) for term in weighted_query)
        query_norm = math.sqrt(sum(value * value for value in weighted_query.values()))
        doc_norm = math.sqrt(sum(value * value for value in doc_vector.values()))
        if query_norm == 0 or doc_norm == 0:
            return 0.0
        return numerator / (query_norm * doc_norm)

    # Adds extra score when words match the title or tags.
    def _metadata_boost(self, query_terms: list[str], document: Document) -> float:
        title_terms = set(_tokenize(document.title))
        tag_terms = {tag.lower() for tag in document.tags}
        boost = 0.0
        for term in query_terms:
            if term in title_terms:
                boost += 0.05
            if term in tag_terms:
                boost += 0.08
        return boost


# Splits text into useful lowercase search words.
def _tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in _TOKEN_RE.findall(text)
        if len(token) > 1 and token.lower() not in _STOPWORDS
    ]
