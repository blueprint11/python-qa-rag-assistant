from dataclasses import dataclass


# Internal format for one Stack Overflow question-answer pair.
@dataclass(frozen=True)
class Document:
    id: str
    title: str
    question: str
    answer: str
    tags: list[str]
    score: int = 0
    source_url: str | None = None

    # Text used by the retriever for searching.
    @property
    def searchable_text(self) -> str:
        tags = " ".join(self.tags)
        return f"{self.title} {tags} {self.question} {self.answer}"

    # Short readable text used in API source snippets.
    @property
    def display_text(self) -> str:
        return f"{self.title}. {self.answer}"
