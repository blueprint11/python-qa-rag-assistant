from __future__ import annotations

import csv
import html
import re
from collections import defaultdict
from pathlib import Path

from app.rag.documents import Document

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


# Removes HTML from Stack Overflow text.
def clean_html(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    text = re.sub(r"<pre><code>(.*?)</code></pre>", r" Code example: \1 ", text, flags=re.S)
    text = _TAG_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


# Loads documents from either the Kaggle folder or the sample CSV.
def load_documents(dataset_path: str, max_documents: int) -> list[Document]:
    path = Path(dataset_path)
    if path.is_dir():
        return _load_kaggle_directory(path, max_documents)
    if path.exists():
        return _load_flat_csv(path, max_documents)

    fallback = Path("data/sample_python_qa.csv")
    return _load_flat_csv(fallback, max_documents)


# Loads our simple sample CSV format.
def _load_flat_csv(path: Path, max_documents: int) -> list[Document]:
    documents: list[Document] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            documents.append(
                Document(
                    id=row.get("id", str(len(documents) + 1)),
                    title=clean_html(row.get("title")),
                    question=clean_html(row.get("question")),
                    answer=clean_html(row.get("answer")),
                    tags=_parse_tags(row.get("tags", "")),
                    score=_safe_int(row.get("score")),
                    source_url=row.get("source_url") or None,
                )
            )
            if len(documents) >= max_documents:
                break
    return documents


# Loads the real Kaggle format: Questions.csv, Answers.csv, Tags.csv.
def _load_kaggle_directory(path: Path, max_documents: int) -> list[Document]:
    questions_path = path / "Questions.csv"
    answers_path = path / "Answers.csv"
    tags_path = path / "Tags.csv"
    if not questions_path.exists() or not answers_path.exists():
        raise FileNotFoundError(
            "Kaggle dataset directory must contain Questions.csv and Answers.csv"
        )

    tags_by_question = _load_tags(tags_path) if tags_path.exists() else {}
    best_answers = _load_best_answers(answers_path)

    documents: list[Document] = []
    with questions_path.open(newline="", encoding="latin-1") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            question_id = row.get("Id", "")
            answer_row = best_answers.get(question_id)
            if not question_id or not answer_row:
                continue

            tags = tags_by_question.get(question_id, ["python"])
            title = clean_html(row.get("Title"))
            answer = clean_html(answer_row.get("Body"))
            question = clean_html(row.get("Body"))
            if not title or not answer:
                continue

            documents.append(
                Document(
                    id=question_id,
                    title=title,
                    question=question,
                    answer=answer,
                    tags=tags,
                    score=_safe_int(row.get("Score")) + _safe_int(answer_row.get("Score")),
                    source_url=f"https://stackoverflow.com/questions/{question_id}",
                )
            )
            if len(documents) >= max_documents:
                break
    return documents


# Finds the highest-scoring answer for each question.
def _load_best_answers(path: Path) -> dict[str, dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="latin-1") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parent_id = row.get("ParentId", "")
            if not parent_id:
                continue
            current = best.get(parent_id)
            if current is None or _safe_int(row.get("Score")) > _safe_int(current.get("Score")):
                best[parent_id] = row
    return best


# Groups tags by question id.
def _load_tags(path: Path) -> dict[str, list[str]]:
    tags: dict[str, list[str]] = defaultdict(list)
    with path.open(newline="", encoding="latin-1") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            question_id = row.get("Id", "")
            tag = row.get("Tag", "")
            if question_id and tag:
                tags[question_id].append(tag)
    return dict(tags)


# Converts raw tag text into a clean list of tags.
def _parse_tags(raw_tags: str) -> list[str]:
    if not raw_tags:
        return []
    raw_tags = raw_tags.replace("|", ",").replace(";", ",")
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


# Safely converts CSV score values into integers.
def _safe_int(value: str | int | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0
