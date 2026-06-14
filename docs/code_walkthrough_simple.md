# Simple Code Walkthrough

Use this for discussion when someone asks what each part does.

## What We Built

This is a RAG app, not an agent.

RAG means:

User question -> search dataset -> pick best answers -> create grounded answer

We do not let the app guess. If it does not find a good match, it returns low confidence.

## Request Flow


POST /ask
  -> routes.py
  -> qa_controller.py
  -> qa_service.py
  -> retriever.py
  -> generator.py


## Files 

`app/main.py`

Starts the FastAPI app.

`app/api/routes.py`

Defines the API URLs: `GET /health` and `POST /ask`.

`app/api/controllers/qa_controller.py`

Receives API requests and sends them to the service.

`app/services/qa_service.py`

Main brain of the app. It calls retriever first, then generator.

`app/repositories/document_repository.py`

Loads the dataset and keeps it in memory.

`app/rag/ingestion.py`

Reads the sample CSV or Kaggle files and cleans the text.

`app/rag/retriever.py`

Searches the dataset and finds the most relevant answers.

`app/rag/generator.py`

Creates the final response from retrieved answers.

`app/models/schemas.py`

Defines request and response formats.

`tests/test_api.py`

Checks if the API works correctly.



I made a FastAPI RAG application. The user sends a Python question to `/ask`. The app searches Stack Overflow Python Q&A data, finds the most relevant answers, and returns a grounded answer with sources. I used controller, service, and repository layers to keep the code organized and easier to test.

## Why It Looks Split Into Many Files

It is split so each file has one job:

- routes handle URLs
- controller handles API request flow
- service handles main logic
- repository handles data loading
- retriever handles search
- generator handles final answer

This makes it cleaner than putting everything in one big file.
