# API Test Results

Dataset used for this run: `data/processed_python_qa_5k.csv`.

This file records manual API testing through the FastAPI `/ask` flow using the processed 5k-row Kaggle Stack Overflow Python Q&A subset. The response was checked for confidence, source grounding, and answer quality.

Health check result:

```json
{
  "status": "ok",
  "document_count": 5000
}
```

## Successful Test Queries

| # | Query | Confidence | Main sources returned | Observed response summary | Quality observation |
|---|---|---|---|---|---|
| 1 | What is a private member of a class in Python? | Medium | `Python "protected" attributes`; `Why are Python's 'private' methods not actually private?` | Explained `_member`, `__member`, protected/private convention, and name mangling. | Good grounded answer. It correctly shows that Python privacy is mostly convention/name mangling. |
| 2 | Python private methods not actually private | High | `Why are Python's 'private' methods not actually private?` | Explained that name mangling prevents accidental subclass override, not deliberate outside access. | Very good match because the top source directly answers the question. |
| 3 | What is the difference between list and tuples in Python? | High | `What's the difference between list and tuples?`; `Python: what is the difference between (1,2,3) and [1,2,3]` | Explained tuple immutability and semantic usage differences. | Good answer with relevant Stack Overflow sources. |
| 4 | How to merge two Python dictionaries in a single expression? | High | `How to merge two Python dictionaries in a single expression?` | Returned dictionary merge guidance using `dict(...)` style examples from the source. | Good source match. Some syntax is older Python style because the dataset contains old Stack Overflow posts. |
| 5 | How do I sort a list of dictionaries by values of the dictionary in Python? | High | `How do I sort a list of dictionaries by values of the dictionary in Python?` | Recommended `sorted(..., key=lambda ...)` style sorting. | Good practical answer and source title exactly matches the question. |
| 6 | Which is better in Python, lambda functions or nested def functions? | High | `Which is more preferable to use in Python: lambda functions or nested functions ('def')?` | Recommended `def` when the function needs a name/readability and lambda only for small anonymous functions. | Good answer, mainly grounded in one strong source. |
| 7 | Generator expressions vs list comprehension in Python | High | `Generator Expressions vs. List Comprehension` | Explained when list comprehensions are useful and when generator expressions avoid building a full list. | Good answer for a common Python learner question. |
| 8 | What are class methods in Python for? | High | `What are Class methods in Python for?` | Explained class methods as methods related to the class rather than a specific instance. | Very good source match and easy to understand. |
| 9 | Do Python regular expressions allow embedded options? | High | `Do Python regular expressions allow embedded options?` | Answered yes and referenced inline regex flags/options. | Good answer because the source directly matches the asked topic. |
| 10 | How do I use the with statement for CSV files in Python? | High | `Using "with" statement for CSV files in Python` | Explained that `with` safely closes files and cleans up resources. | Good answer and useful for file-handling learners. |

## Failure Cases And Edge Cases Observed

| Edge case | Observed behavior | Quality observation |
|---|---|---|
| `How do I tune a guitar?` | Returned low confidence, no sources, and asked for a Python/library/error-message query. | Correct behavior. The system did not hallucinate a Python answer for a non-Python question. |
| `How do I fix ModuleNotFoundError in Python?` | Returned low confidence and no sources after the confidence threshold was raised. | Acceptable limitation. The 5k subset is from older Stack Overflow data and did not contain a strong `ModuleNotFoundError` match. |
| `How do I learn Python?` | Retrieved sources, but the answer was broad and partly dated because the dataset contains older Python 2/Python 3 migration content. | This shows a RAG limitation: broad questions need better semantic search, fresher data, or curated learning resources. |

## Overall Notes

- The system gives the best answers when the question has specific Python terms that appear in the dataset, such as `tuple`, `lambda`, `class methods`, or `with statement`.
- Exact or near-exact Stack Overflow-style questions produce high-confidence grounded responses.
- The current retriever is keyword/TF-IDF style, not semantic embeddings. This keeps deployment cheap and simple, but semantic paraphrases may be weaker.
- Raising `MIN_RETRIEVAL_SCORE` to `0.25` helped reduce weak low-confidence answers with irrelevant sources.
- For a production version, I would use embeddings plus a vector database and a reranker to improve answer quality for paraphrased or broad learner questions.
