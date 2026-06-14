# Python Programming Q&A Assistant - Slide Deck

## 1. Problem Statement
- Data science learners ask many Python questions while practicing.
- They need answers that are grounded in reliable examples, not made-up responses.
- Goal: build a public FastAPI Q&A service using the Stack Overflow Python Q&A Kaggle dataset.

## 2. What I Built
- A FastAPI-based Python Q&A assistant.
- `GET /health` checks whether the API is running.
- `POST /ask` accepts a Python question and returns an answer, confidence, sources, and limitations.
- The app uses a processed 5k-row Kaggle subset for reliable free-tier deployment.

## 3. RAG Pipeline
```text
User question
  -> clean/tokenize question
  -> retrieve matching Stack Overflow Q&A documents
  -> rank top sources
  -> generate answer from retrieved sources
  -> return answer + confidence + citations
```
- This is RAG, not an agent.
- No tool planning or multi-step agent workflow is needed for this dataset search task.

## 4. Architecture Diagram
```text
Client / Swagger UI
        |
        v
FastAPI routes.py
        |
        v
QAController
        |
        v
QAService
   |            |
   v            v
DocumentRepository   GroundedAnswerGenerator
   |
   v
KeywordRetriever over processed Kaggle documents
```

## 5. Dataset Design
- Source dataset: Kaggle `stackoverflow/pythonquestions`.
- Raw files: `Questions.csv`, `Answers.csv`, `Tags.csv`.
- Preparation script creates `data/processed_python_qa_5k.csv`.
- Each processed row contains question title, body, best answer, tags, score, and Stack Overflow URL.

## 6. Key Design Decisions
- Used FastAPI because it gives automatic Swagger docs and easy API testing.
- Used controller/service/repository structure so each file has one job.
- Used a custom lightweight RAG pipeline instead of LangChain/LlamaIndex to keep the project simple and explainable.
- Used a 5k processed Kaggle subset for stable free deployment.

## 7. Retrieval And Grounding
- Current retrieval is keyword/TF-IDF style with cosine similarity.
- Title and tag matches receive a small boost.
- If the top score is below `MIN_RETRIEVAL_SCORE`, the app returns a low-confidence fallback.
- Every good answer includes sources so the user can see where the answer came from.

## 8. Testing Results
- API tests cover health check, successful answer, validation, and low-confidence fallback.
- Manual test report includes 10 successful Python queries.
- Edge cases tested: non-Python query, broad query, and missing/old terminology query.
- Result file: `docs/test_results.md`.

## 9. Scaling To 100+ Concurrent Users
- Latency: pre-build the index at deploy time instead of rebuilding per request.
- Async calls: keep FastAPI endpoints async if an external LLM or vector DB is added.
- Database: move documents and embeddings to pgvector, Qdrant, Pinecone, or FAISS.
- Caching: cache frequent questions and retrieval results in Redis.
- Serving: run multiple Uvicorn workers behind a load balancer.
- Cost: use a cheap retriever first, call an LLM only for final synthesis when needed.

## 10. Deployment
- Public app is deployed on Render.
- Live URL: `https://python-qa-rag-assistant.onrender.com`
- Swagger UI: `https://python-qa-rag-assistant.onrender.com/docs`
- Health check confirms `document_count = 5000`.
- Free tier note: first request can be slower because Render may spin down after inactivity.
