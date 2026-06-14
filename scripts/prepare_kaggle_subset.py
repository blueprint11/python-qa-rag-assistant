import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.ingestion import load_documents


# Writes the processed CSV format that the deployed app can load quickly.
def write_processed_csv(input_dir: str, output_file: str, max_documents: int) -> None:
    input_path = Path(input_dir)
    required_files = ["Questions.csv", "Answers.csv", "Tags.csv"]
    missing_files = [name for name in required_files if not (input_path / name).exists()]
    if missing_files:
        missing_text = ", ".join(missing_files)
        raise FileNotFoundError(
            f"Missing Kaggle files in {input_path}: {missing_text}. "
            "Download and unzip the Kaggle dataset into data/kaggle first."
        )

    documents = load_documents(input_dir, max_documents)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "title", "question", "answer", "tags", "score", "source_url"],
        )
        writer.writeheader()
        for document in documents:
            writer.writerow(
                {
                    "id": document.id,
                    "title": document.title,
                    "question": document.question,
                    "answer": document.answer,
                    "tags": ",".join(document.tags),
                    "score": document.score,
                    "source_url": document.source_url or "",
                }
            )

    print(f"Wrote {len(documents)} documents to {output_path}")


# Command line entry point.
def main() -> None:
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "data/kaggle"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/processed_python_qa_5k.csv"
    max_documents = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    write_processed_csv(input_dir, output_file, max_documents)


if __name__ == "__main__":
    main()
