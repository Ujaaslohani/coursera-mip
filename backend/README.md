# Coursera MIP Backend

FastAPI backend for orchestrating the advanced `rag` retrieval/synthesis pipeline and saving application activity to Supabase.

Current backend status: **rag retrieval/synthesis delegation is done. Supabase application persistence is done.** Media processing and embedding-refresh jobs are still pending.

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

Run the end-to-end Supabase application-flow smoke test:

```bash
backend\.venv\Scripts\python backend\scripts\smoke_supabase_flow.py
```

This verifies:

```text
Supabase schema health
conversation insert
RAG/Qdrant context retrieval
query/response/evidence/recommendation insert
feedback insert
dashboard aggregation
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

Delegates retrieval to `rag.retreival.pipeline`, which owns hybrid retrieval, BM25, vector retrieval, fusion, and reranking. Requires `COHERE_API_KEY`.

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
  "filters": {}
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

Delegates retrieval to `rag.retreival.pipeline` and returns normalized, LLM-ready evidence. Requires `COHERE_API_KEY`.

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

### `GET /api/supabase/health`

Checks Supabase connectivity and confirms required tables/views exist.

Request:

```bash
curl http://localhost:8000/api/supabase/health
```

Response:

```json
{
  "status": "ok",
  "configured": true,
  "url": "https://nodicagzdyqrzkysvjkb.supabase.co",
  "tables_found": ["conversations", "user_queries"],
  "missing_tables": []
}
```

### `GET /api/supabase/tables`

Lists tables and dashboard views exposed by Supabase REST.

Request:

```bash
curl http://localhost:8000/api/supabase/tables
```

Response:

```json
{
  "tables": [
    "conversations",
    "user_queries",
    "generated_responses",
    "retrieval_evidence",
    "recommendations",
    "user_feedback"
  ]
}
```

### `POST /api/conversations`

Creates a conversation/session row in Supabase.

Request body:

```json
{
  "session_id": "frontend-session-id",
  "title": "Course help",
  "user_id": null,
  "metadata": {
    "source": "frontend"
  }
}
```

Response:

```json
{
  "conversation_id": "uuid",
  "session_id": "frontend-session-id",
  "title": "Course help",
  "user_id": null,
  "started_at": "2026-08-26T16:26:12.274936+00:00",
  "last_activity_at": "2026-08-26T16:26:12.274936+00:00",
  "metadata": {
    "source": "frontend"
  }
}
```

### `GET /api/conversations`

Lists recent conversations from Supabase.

Query params:

- `limit`: default `20`, max `100`

Request:

```bash
curl "http://localhost:8000/api/conversations?limit=10"
```

Response:

```json
[
  {
    "conversation_id": "uuid",
    "session_id": "frontend-session-id",
    "title": "Course help",
    "user_id": null,
    "started_at": "2026-08-26T16:26:12.274936+00:00",
    "last_activity_at": "2026-08-26T16:26:12.274936+00:00",
    "metadata": {}
  }
]
```

### `POST /api/interactions`

Saves one complete RAG interaction to Supabase: query, generated answer, Qdrant evidence references, and recommendations.

Request body:

```json
{
  "conversation_id": "uuid",
  "query_text": "Why are learners confused about regularization?",
  "generated_answer": "Learners appear to confuse...",
  "normalized_topic": "regularization",
  "detected_intent": "friction_analysis",
  "model_name": "your-llm-model",
  "model_provider": "your-llm-provider",
  "evidence": [
    {
      "point_id": "qdrant-point-id",
      "content_type": "caption",
      "lecture_id": "lec13",
      "module_id": "MOD_13",
      "score": 0.91,
      "retrieval_rank": 1,
      "text": "Retrieved evidence text..."
    }
  ],
  "recommendations": [
    {
      "recommendation_type": "content_improvement",
      "recommendation_text": "Add a clearer example...",
      "target_record_id": "qdrant-point-id",
      "priority": 1
    }
  ],
  "metadata": {}
}
```

Response:

```json
{
  "conversation_id": "uuid",
  "query_id": "uuid",
  "response_id": "uuid",
  "evidence_count": 1,
  "recommendation_count": 1
}
```

### `POST /api/feedback`

Stores user/reviewer feedback for a generated response.

Request body:

```json
{
  "response_id": "uuid",
  "user_id": null,
  "rating": 5,
  "is_helpful": true,
  "approval": "approved",
  "feedback_text": "Useful answer."
}
```

Response:

```json
{
  "feedback_id": "uuid",
  "response_id": "uuid",
  "rating": 5,
  "is_helpful": true,
  "approval": "approved"
}
```

### `GET /api/dashboard/summary`

Reads Supabase dashboard views for application analytics.

Request:

```bash
curl http://localhost:8000/api/dashboard/summary
```

Response:

```json
{
  "activity_summary": {
    "total_conversations": 3,
    "total_queries": 2,
    "total_responses": 2,
    "total_evidence_records": 2,
    "total_recommendations": 2,
    "total_feedback_records": 2
  },
  "popular_topics": [],
  "evidence_usage": [],
  "lecture_usage": [],
  "feedback_summary": {}
}
```

## Newly Completed Original Endpoints

### `POST /api/assets`

Registers an asset in the backend-local operations store and creates an initial `uploaded` job.

Request body:

```json
{
  "modality": "transcript",
  "owner": "content-team@coursera.org",
  "topic": "Regularization",
  "concept_tags": ["overfitting"],
  "storage_url": "s3-or-local-or-source-reference",
  "permission_scope": ["course:deeplearning"],
  "metadata": {}
}
```

Response:

```json
{
  "asset_id": "uuid",
  "job_id": "uuid",
  "status": "uploaded",
  "duplicate": false
}
```

### `GET /api/assets/registered`

Lists assets registered through `POST /api/assets`.

Response:

```json
[
  {
    "asset_id": "uuid",
    "modality": "transcript",
    "owner": "content-team@coursera.org",
    "topic": "Regularization",
    "storage_url": "s3-or-local-or-source-reference",
    "status": "uploaded",
    "created_at": "2026-08-26T16:33:39.909191+00:00"
  }
]
```

### `POST /api/processing-jobs`

Creates a processing lifecycle record for a registered asset. Current implementation records state only; actual media preprocessing remains in the database/AI pipeline.

Request body:

```json
{
  "asset_id": "uuid"
}
```

Response:

```json
{
  "job_id": "uuid",
  "asset_id": "uuid",
  "stage": "searchable",
  "error": null,
  "warnings": ["Backend records lifecycle state only; media preprocessing is handled by the database/AI pipeline."],
  "created_at": "2026-08-26T16:33:39.909191+00:00",
  "updated_at": "2026-08-26T16:33:39.909191+00:00"
}
```

### `GET /api/processing-jobs/{job_id}`

Fetches processing lifecycle state for one job.

### `POST /api/processing-jobs/{job_id}/archive`

Marks a processing job as `archived`.

### `POST /api/embeddings`

Verifies existing Qdrant points and confirms whether their payloads match the expected embedding model/dimensions. It does not mutate vectors.

Request body:

```json
{
  "segment_ids": ["0018fed9-e6dd-5b0b-81f3-bd4c1e0458fe"],
  "qdrant_record_ids": []
}
```

Response:

```json
{
  "requested_count": 1,
  "verified_count": 1,
  "updated_count": 0,
  "skipped_count": 0,
  "status": "verified_existing_embeddings",
  "details": [
    {
      "point_id": "0018fed9-e6dd-5b0b-81f3-bd4c1e0458fe",
      "exists": true,
      "verified": true,
      "embedding_model": "BAAI/bge-base-en-v1.5"
    }
  ]
}
```

### `POST /api/synthesize`

Creates a grounded insight by calling `rag.synthesis.synthesize_insight`. There is no backend static fallback. Requires `COHERE_API_KEY` when retrieval is needed and `GROQ_API_KEY` for synthesis. The result is persisted to Supabase.

Request body:

```json
{
  "query": "Why are learners confused about adversarial training?",
  "conversation_id": null,
  "session_id": "frontend-session-id",
  "top_k": 5,
  "filters": {},
  "metadata": {
    "normalized_topic": "adversarial training"
  }
}
```

Response:

```json
{
  "insight_id": "uuid",
  "conversation_id": "uuid",
  "query_id": "uuid",
  "answer_text": "Summary: ...",
  "citations": [
    {
      "point_id": "qdrant-point-id",
      "content_type": "caption",
      "lecture_id": "lec17",
      "score": 0.79,
      "text_preview": "..."
    }
  ],
  "confidence": 0.79,
  "status": "pending_review"
}
```

### `GET /api/insights`

Lists generated responses saved in Supabase.

Query params:

- `status`: optional. Supports Supabase response statuses like `completed`, and metadata statuses like `pending_review`.
- `limit`: default `50`, max `100`

### `GET /api/insights/{insight_id}`

Returns one insight with its query, generated response, evidence references, recommendations, and feedback.

### `POST /api/review-feedback`

Stores review feedback for an insight. This is an alias-style endpoint over Supabase `user_feedback`.

Request body:

```json
{
  "insight_id": "uuid",
  "decision": "approved",
  "notes": "Evidence is grounded.",
  "rating": 5,
  "is_helpful": true,
  "user_id": null
}
```

Response:

```json
{
  "feedback_id": "uuid",
  "response_id": "uuid",
  "rating": 5,
  "is_helpful": true,
  "approval": "approved"
}
```

## Original Endpoint Coverage

All original route names now exist.

| Original endpoint | Current implementation |
|---|---|
| `POST /api/assets` | Registers an asset and creates an initial `uploaded` job in `backend/.data/operations.json`. |
| `GET /api/assets` | Returns Qdrant-indexed asset summaries. Use `GET /api/assets/registered` for locally registered assets. |
| `POST /api/processing-jobs` | Creates a backend job record and marks the registered asset `searchable`. Actual media preprocessing remains in the database/AI pipeline. |
| `GET /api/processing-jobs/{job_id}` | Reads job status from the backend-local operations store. |
| `POST /api/processing-jobs/{job_id}/archive` | Archives a backend-local job record. |
| `POST /api/embeddings` | Verifies existing Qdrant points use the expected embedding model/dimensions. It does not mutate Qdrant vectors. |
| `POST /api/query` | Delegates to `rag.retreival.pipeline`; backend no longer has duplicate dense search. |
| `POST /api/synthesize` | Delegates to `rag.synthesis.synthesize_insight`; backend no longer has static synthesis fallback. |
| `GET /api/insights` | Lists generated Supabase responses. |
| `GET /api/insights/{insight_id}` | Reads a generated response plus query, evidence, recommendations, and feedback from Supabase. |
| `GET /api/segments/{segment_id}` | Fetches one Qdrant point by ID. |
| `POST /api/review-feedback` | Stores review feedback in Supabase `user_feedback`. |
| `GET /api/metrics` | Returns Qdrant health and payload counts. |

## Remaining Caveats

Supabase currently stores conversations, queries, generated responses, evidence, recommendations, feedback, and dashboard views. It does not currently define `assets`, `processing_jobs`, or `audit_log` tables.

Because of that, asset registration and processing-job state are stored locally in:

```text
backend/.data/operations.json
```

That file is ignored by git. For production deployment, add these optional Supabase tables and then swap `backend/app/services/operations_store.py` to write to Supabase instead:

- `assets`: `asset_id`, `modality`, `owner`, `topic`, `storage_url`, `permission_scope`, `status`, `created_at`, `metadata`
- `processing_jobs`: `job_id`, `asset_id`, `stage`, `error`, `warnings`, `created_at`, `updated_at`
- `audit_log`: `id`, `action`, `resource_type`, `resource_id`, `details_json`, `created_at`

Qdrant vector mutation is intentionally not performed by `POST /api/embeddings` yet. The endpoint validates existing indexed points. A true embedding refresh should be added only when the backend owns source text, deterministic point IDs, payload schema validation, and a safe Qdrant upsert policy.

For now, the backend can orchestrate rag retrieval/synthesis, persist full RAG activity to Supabase, expose insights/reviews, and provide the original endpoint names needed by the frontend and LLM layer.
