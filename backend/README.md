# Coursera MIP Backend

FastAPI backend for fetching, inspecting, and semantically querying records from the existing Qdrant collection.

Current backend status: **Qdrant retrieval layer is done.** Asset registration, job processing, insight persistence, and human review workflows are still pending.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill `.env` with the Qdrant URL, collection name, and API key. Keep real secrets out of git.

Manual install command from the repo root:

```bash
python -m venv backend\.venv
backend\.venv\Scripts\python -m pip install -r backend\requirements.txt
```

## Run

From inside `backend`:

```bash
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

From the repo root:

```bash
backend\.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000
```

API docs are available at `http://localhost:8000/docs`.

## Smoke Test

Run this before starting the API to verify Qdrant access:

```bash
backend\.venv\Scripts\python backend\scripts\smoke_qdrant.py
```

Expected result shape:

```text
collection=COURSEERA_ALMAX_MULTIMODAL
status=green
points_count=5285
sample_records=3
```

## Done Endpoints

### `GET /health`

Checks that the backend is running and shows the active Qdrant collection/model config.

Request:

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "ok",
  "qdrant_url_configured": true,
  "qdrant_collection": "COURSEERA_ALMAX_MULTIMODAL",
  "embedding_model": "BAAI/bge-base-en-v1.5"
}
```

### `GET /api/qdrant/collection`

Fetches live Qdrant collection metadata.

Request:

```bash
curl http://localhost:8000/api/qdrant/collection
```

Response:

```json
{
  "collection_name": "COURSEERA_ALMAX_MULTIMODAL",
  "status": "green",
  "vectors_count": null,
  "points_count": 5285,
  "indexed_vectors_count": 0,
  "config": {
    "params": {
      "vectors": {
        "size": 768,
        "distance": "Cosine"
      }
    }
  }
}
```

### `GET /api/qdrant/records`

Scrolls raw Qdrant records without running embeddings. Useful for checking what payload fields exist.

Query params:

- `limit`: number of records, default `10`, max `100`
- `offset`: optional Qdrant scroll offset from the previous response

Request:

```bash
curl "http://localhost:8000/api/qdrant/records?limit=2"
```

Response:

```json
{
  "records": [
    {
      "id": "0018fed9-e6dd-5b0b-81f3-bd4c1e0458fe",
      "payload": {
        "record_id": "lec04_caption_chunk_63",
        "asset_id": "VIDEO_LEC04",
        "course_id": "deeplearning",
        "lecture_id": "lec04",
        "content_type": "caption",
        "text": "..."
      }
    }
  ],
  "next_page_offset": "..."
}
```

### `GET /api/qdrant/records/{point_id}`

Fetches one exact Qdrant point by ID.

Request:

```bash
curl http://localhost:8000/api/qdrant/records/0018fed9-e6dd-5b0b-81f3-bd4c1e0458fe
```

Response:

```json
{
  "id": "0018fed9-e6dd-5b0b-81f3-bd4c1e0458fe",
  "payload": {
    "record_id": "lec04_caption_chunk_63",
    "asset_id": "VIDEO_LEC04",
    "content_type": "caption",
    "text": "..."
  }
}
```

### `GET /api/evidence/{point_id}`

Evidence-friendly alias for fetching one record. The LLM/frontend can use this route when a citation needs to be inspected.

Request:

```bash
curl http://localhost:8000/api/evidence/0018fed9-e6dd-5b0b-81f3-bd4c1e0458fe
```

Response: same shape as `GET /api/qdrant/records/{point_id}`.

### `POST /api/query`

Embeds the user question with `BAAI/bge-base-en-v1.5` and performs semantic vector search in Qdrant.

Request:

```bash
curl -X POST http://localhost:8000/api/query ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"learners are confused about adversarial training\",\"top_k\":2}"
```

Request body:

```json
{
  "query": "learners are confused about adversarial training",
  "top_k": 2,
  "filters": {
    "content_type": "caption"
  }
}
```

Response:

```json
{
  "query": "learners are confused about adversarial training",
  "top_k": 2,
  "collection_name": "COURSEERA_ALMAX_MULTIMODAL",
  "results": [
    {
      "id": "19fd8be8-57aa-5748-8d59-5081b14483c8",
      "score": 0.79173136,
      "text": "given that perturbation...",
      "payload": {
        "asset_id": "VIDEO_LEC17",
        "course_id": "deeplearning",
        "lecture_id": "lec17",
        "content_type": "caption"
      }
    }
  ]
}
```

### `POST /api/context`

Runs semantic search and returns normalized, LLM-ready evidence. This is the best endpoint for the LLM layer.

Request:

```bash
curl -X POST http://localhost:8000/api/context ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"learners are confused about adversarial training\",\"top_k\":2}"
```

Request body:

```json
{
  "query": "learners are confused about adversarial training",
  "top_k": 2,
  "filters": {}
}
```

Response:

```json
{
  "query": "learners are confused about adversarial training",
  "evidence_count": 2,
  "context": [
    {
      "point_id": "19fd8be8-57aa-5748-8d59-5081b14483c8",
      "score": 0.79173136,
      "source_id": null,
      "asset_id": "VIDEO_LEC17",
      "content_type": "caption",
      "course_id": "deeplearning",
      "lecture_id": "lec17",
      "timestamp": "1826.0-1908.0s",
      "text": "given that perturbation...",
      "payload": {}
    }
  ]
}
```

### `GET /api/metadata/options`

Scans Qdrant payloads and returns available filter values for UI dropdowns.

Query params:

- `scan_limit`: number of Qdrant records to scan, default `5000`, max `10000`

Request:

```bash
curl "http://localhost:8000/api/metadata/options?scan_limit=1000"
```

Response:

```json
{
  "content_types": ["caption", "discussion", "frame", "quiz", "slide"],
  "course_ids": ["deeplearning"],
  "lecture_ids": ["lec01", "lec02", "lec04"],
  "concept_tags": ["Adversarial training"],
  "friction_types": ["Confusion"],
  "embedding_models": ["BAAI/bge-base-en-v1.5"],
  "scanned_records": 1000
}
```

### `GET /api/assets`

Groups indexed Qdrant segments by `asset_id` and returns asset summaries.

Query params:

- `limit`: number of asset summaries to return, default `50`, max `500`
- `scan_limit`: number of Qdrant records to scan, default `5000`, max `10000`

Request:

```bash
curl "http://localhost:8000/api/assets?limit=3&scan_limit=1000"
```

Response:

```json
{
  "assets": [
    {
      "asset_id": "VIDEO_LEC24",
      "content_type": "caption",
      "course_id": "deeplearning",
      "lecture_id": "lec24",
      "segment_count": 5,
      "sample_point_id": "00d4d977-2ddb-5d41-b26b-b20ce8f268cf",
      "sample_text": "sampling..."
    }
  ],
  "scanned_records": 1000
}
```

### `GET /api/metrics`

Returns Qdrant health plus lightweight content/course/model counts.

Query params:

- `scan_limit`: number of Qdrant records to scan, default `5000`, max `10000`

Request:

```bash
curl "http://localhost:8000/api/metrics?scan_limit=1000"
```

Response:

```json
{
  "collection_name": "COURSEERA_ALMAX_MULTIMODAL",
  "qdrant_status": "green",
  "points_count": 5285,
  "scanned_records": 1000,
  "content_type_counts": {
    "frame": 300,
    "slide": 250,
    "caption": 200
  },
  "course_id_counts": {
    "deeplearning": 1000
  },
  "embedding_model_counts": {
    "BAAI/bge-base-en-v1.5": 1000
  }
}
```

## Original Endpoint Coverage

Done or partially done:

| Original endpoint | Current status |
|---|---|
| `GET /api/assets` | Done as Qdrant asset summaries. |
| `POST /api/query` | Done as BGE + Qdrant semantic retrieval. |
| `GET /api/metrics` | Done as Qdrant health and payload counts. |
| `GET /api/segments/{segment_id}` | Partially covered by `GET /api/evidence/{point_id}` and `GET /api/qdrant/records/{point_id}`. |

Not done yet:

| Original endpoint | What is missing |
|---|---|
| `POST /api/assets` | Needs a backend asset store for registered uploads/assets. |
| `POST /api/processing-jobs` | Needs job records and processing lifecycle state. |
| `GET /api/processing-jobs/{job_id}` | Needs persisted job status lookup. |
| `POST /api/embeddings` | Needs a controlled embedding refresh pipeline and Qdrant upsert path. |
| `POST /api/synthesize` | Needs LLM integration and insight persistence. |
| `GET /api/insights/{insight_id}` | Needs stored insight records. |
| `POST /api/review-feedback` | Needs stored review decisions and insight status updates. |

## How To Build What Is Left

Recommended next backend layer: add a small SQLite database inside `backend/` for operational state while keeping Qdrant as the vector/evidence store.

Suggested tables:

- `assets`: `asset_id`, `modality`, `owner`, `topic`, `storage_url`, `permission_scope`, `created_at`
- `processing_jobs`: `job_id`, `asset_id`, `stage`, `error`, `created_at`, `updated_at`
- `insights`: `insight_id`, `query`, `answer_text`, `citations_json`, `confidence`, `status`, `created_at`
- `review_feedback`: `feedback_id`, `insight_id`, `decision`, `notes`, `created_at`
- `audit_log`: `id`, `action`, `resource_type`, `resource_id`, `details_json`, `created_at`

Implementation order:

1. Add `backend/app/database.py` with SQLite connection and table creation.
2. Add `POST /api/assets` to create an asset row and initial `uploaded` job.
3. Add `POST /api/processing-jobs` and `GET /api/processing-jobs/{job_id}` for lifecycle tracking.
4. Add `POST /api/synthesize` to accept evidence from `/api/context`, call the existing LLM layer, and store an insight.
5. Add `GET /api/insights/{insight_id}` to return stored insight output and citations.
6. Add `POST /api/review-feedback` to store human review decisions.
7. Add `POST /api/embeddings` last, because it mutates the vector DB and should validate dimensions, payload schema, duplicate point IDs, and permissions first.

For now, the backend is ready for the frontend/LLM layer to retrieve real evidence through `/api/query`, `/api/context`, and `/api/evidence/{point_id}`.
