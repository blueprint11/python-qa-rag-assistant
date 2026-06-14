# Python Programming Q&A Assistant

AI-powered FastAPI service that answers Python programming questions with grounded sources from a Stack Overflow-style Q&A index.

## Decisions And Tradeoffs

- **FastAPI + controller/service/repository layout**: keeps API, business logic, and data loading separate. This is slightly more files than a single `main.py`, but it is cleaner to test and easier to scale.
- **Retrieval-first RAG**: every answer is built from retrieved documents and returns citations. This reduces hallucination, but answer quality depends on dataset coverage.
- **Deterministic keyword retriever**: cheap, fast, and stable for tests/free-tier deployment. The tradeoff is weaker semantic matching than embeddings or LLM reranking.
- **Processed Kaggle subset committed**: the app uses `data/processed_python_qa_5k.csv`, built from the Kaggle Stack Overflow Python Q&A dataset, so public deployment is fast and reliable.

## Project Structure

```text
app/
  api/controllers/      HTTP controller layer
  core/                 settings and configuration
  models/               request/response schemas
  rag/                  ingestion, retrieval, answer generation
  repositories/         dataset access
  services/             QA orchestration
data/                   sample data and processed Kaggle 5k dataset
docs/                   test results and slide deck
tests/                  FastAPI tests
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

If your system only exposes `python`, replace `python3` with `python`. On Windows, use `py -m venv .venv` and `py -m pip install -r requirements.txt`.

Open:

- Health: `http://127.0.0.1:8000/health`
- Docs: `http://127.0.0.1:8000/docs`

## API

### `GET /health`

Returns service status and indexed document count.

### `POST /ask`

Request:

```json
{
  "question": "How do I read a CSV file in Python?",
  "top_k": 4
}
```

Response:

```json
{
  "question": "How do I read a CSV file in Python?",
  "answer": "Based on the closest Stack Overflow match...",
  "confidence": "high",
  "sources": [
    {
      "id": "1",
      "title": "How do I read a CSV file in Python?",
      "score": 0.77,
      "tags": ["csv", "pandas", "file-io"],
      "snippet": "...",
      "source_url": "https://stackoverflow.com/questions/1"
    }
  ],
  "limitations": []
}
```

## Using The Kaggle Dataset

Download the dataset from Kaggle:

https://www.kaggle.com/datasets/stackoverflow/pythonquestions

Extract it so the directory contains:

- `Questions.csv`
- `Answers.csv`
- `Tags.csv`

For local full-dataset testing, set:

```bash
DATASET_PATH=data/kaggle
MAX_DOCUMENTS=5000
```

The loader joins each question with its highest-scoring answer and tags.

### Create The 5k Deployment Dataset

For free public hosting, create a smaller processed Kaggle subset:

```bash
python3 scripts/prepare_kaggle_subset.py data/kaggle data/processed_python_qa_5k.csv 5000
```

Then set this for deployment:

```bash
DATASET_PATH=data/processed_python_qa_5k.csv
MAX_DOCUMENTS=5000
```

Why this is used for deployment: the data still comes from Kaggle, but the cloud server does not need to download and clean the full raw dataset on every restart.

## Tests

```bash
pytest
```

Documented manual test results are in [docs/test_results.md](docs/test_results.md).

A beginner-friendly code walkthrough is in [docs/code_walkthrough_simple.md](docs/code_walkthrough_simple.md).

The slide deck is in [docs/Python_QA_Assistant_Slide_Deck.pptx](docs/Python_QA_Assistant_Slide_Deck.pptx). Markdown backup content is in [docs/slide_deck.md](docs/slide_deck.md).

## Submission Artifacts

- GitHub repository: code, README, `.env.example`, tests, and processed Kaggle 5k dataset.
- Test results: [docs/test_results.md](docs/test_results.md).
- Slide deck: [docs/Python_QA_Assistant_Slide_Deck.pptx](docs/Python_QA_Assistant_Slide_Deck.pptx).
- Public app URL: add it below after deployment.

## Deployment

### Render

1. Push this repository to GitHub.
2. Create a Render Web Service from the GitHub repo.
3. Use this build command:

```bash
pip install -r requirements.txt
```

4. Use this start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Configure environment variables from `.env.example`.

Render can also read `render.yaml`, which already contains the same build command, start command, and environment variables.

### Hugging Face Spaces

Use Docker Space. The included `Dockerfile` starts FastAPI on port `7860` and loads:

```text
DATASET_PATH=data/processed_python_qa_5k.csv
```

Add the deployed URL here:

```text
Live URL: pending deployment
```
