# API Documentation

Base URL: `http://localhost:8000` (local), `https://coursera-multimodal-intelligence-platform.onrender.com` (live) — see `deployment/backend_hosting.md` for hosting details, including a known free-tier memory limitation that can cause transient `502`s.

All routes require `Authorization: Bearer <token>`. Beyond authentication, every
mutating route also requires a specific **RBAC permission** (see table below) —
an authenticated request with the wrong role gets `403`, not `200`. Every
mutating call is also written to `audit_log` (see `GET /api/audit-log`).

## Roles & permissions

| Role | Permissions |
|---|---|
| `admin` | everything |
| `content-team` | `assets:write`, `processing:write` |
| `educator` | `query:run`, `insights:read` |
| `reviewer` | `query:run`, `insights:read`, `review:write` |
| `analyst` | `metrics:read`, `audit:read` |

## POST /api/assets

Register a new video, image, slide, transcript, quiz, or discussion asset. Requires `assets:write`.

```json
// Request
{
  "modality": "video",
  "owner": "content-team@coursera.org",
  "topic": "Backpropagation",
  "concept_tags": ["neural-networks"],
  "storage_url": "data/sample_assets/course_neural_networks/backprop_lecture.mp4",
  "permission_scope": ["course:neural-networks-101"]
}
// Response
{ "asset_id": "uuid", "job_id": "uuid", "status": "uploaded", "duplicate": false }
```

Re-registering the same `owner` + `modality` + `storage_url` returns the existing asset with `"duplicate": true` instead of creating a copy.

## GET /api/assets/check-storage

Lightweight pre-flight check so the Asset Intake form can warn about a typo'd path before registering an asset that will fail at processing time. Requires `assets:write`.

```
GET /api/assets/check-storage?storage_url=data/sample_assets/.../file.mp4
```
```json
{ "storage_url": "data/sample_assets/.../file.mp4", "exists": true }
```

## GET /api/assets

Every asset with its most recent processing stage — backs the Processing Monitor's processed/unprocessed list. Requires `processing:write`.

```json
[
  {
    "asset_id": "uuid",
    "modality": "video",
    "owner": "content-team@coursera.org",
    "topic": "Backpropagation",
    "job_id": "uuid",
    "stage": "searchable",
    "created_at": "2026-08-02T14:50:37.976374"
  }
]
```

## POST /api/processing-jobs

Runs the full ingestion pipeline synchronously for one asset — resolves the file (via the storage abstraction), preprocesses it per modality, embeds it (OpenAI text embeddings + real CLIP visual embeddings for images), and writes `Segment` rows. Requires `processing:write`.

```json
// Request
{ "asset_id": "uuid" }
// Response
{ "job_id": "uuid", "asset_id": "uuid", "stage": "searchable", "error": null }
```

`stage` is one of the full 9-value lifecycle: `uploaded, preprocessed, embedded, indexed, searchable, retrieved, synthesized, reviewed, archived` (plus `failed`). A job that can't actually be processed (missing `ffmpeg`/`tesseract`, unresolvable file) goes to `failed` with a human-readable `error` — never silently skipped.

## GET /api/processing-jobs/{job_id}

Retrieve job status, stage, and any error. Requires `processing:write`.

```json
{ "job_id": "uuid", "asset_id": "uuid", "stage": "indexed", "error": null }
```

## POST /api/processing-jobs/{job_id}/archive

Manually retires a job — the only lifecycle stage that's never automatic. Requires `processing:write`.

```json
// Response
{ "job_id": "uuid", "asset_id": "uuid", "stage": "archived", "error": null }
```

## POST /api/embeddings

Generate or refresh embeddings for approved asset segments. Requires `processing:write`.

```json
// Request
{ "segment_ids": ["uuid", "uuid"] }
// Response
{ "updated_count": 2 }
```

## POST /api/query

Accept a unified user question and run the retrieval agent pipeline: a Retrieval Planner agent (real `gpt-4o-mini` call) decides search strategy, then permission-aware retrieval runs **two independent searches at once** — text-meaning (OpenAI embeddings) and visual-meaning (CLIP, for images) — merged and re-ranked by an Evidence Ranker agent for cross-modal diversity. Requires `query:run`.

```json
// Request
{ "question_text": "Why are learners struggling with backpropagation?", "top_k": 10 }
// Response
{
  "query_id": "uuid",
  "retrieved_evidence": [
    {
      "segment_id": "uuid",
      "asset_id": "uuid",
      "modality": "discussion",
      "text_content": "...",
      "timestamp_start": null,
      "timestamp_end": null,
      "similarity": 0.81,
      "permitted": true,
      "match_type": "text"
    }
  ],
  "agent_plan": {
    "search_terms": "learners struggling backpropagation concept",
    "top_k": 10,
    "reasoning": "The question is moderately specific..."
  }
}
```

`match_type` is `"text"` (matched by word meaning) or `"visual"` (matched by CLIP on an image's actual pixels, independent of any OCR'd text). Every returned segment's asset advances to `JobStage.retrieved`.

## POST /api/synthesize

Generate a grounded insight pack from retrieved evidence. The LLM (`gpt-4o-mini`) sees only the evidence array below — never the full database. A Quality Validator agent then strips any citation that doesn't map to a retrieved `segment_id` and caps confidence if it had to. Requires `query:run`.

```json
// Request
{ "query_id": "uuid", "retrieved_evidence": [ /* from /api/query */ ] }
// Response
{ "insight_id": "uuid", "answer_text": "...", "citations": [ { "segment_id": "uuid", "reason": "..." } ], "confidence": 0.74, "status": "pending_review" }
```

Cited assets advance to `JobStage.synthesized`.

## GET /api/insights

List insights, optionally filtered by `status` (e.g. `pending_review`) — backs the Recommendation Workspace's browsable review queue. Requires `insights:read`.

```
GET /api/insights?status=pending_review&limit=50
```
```json
[
  {
    "insight_id": "uuid",
    "query_id": "uuid",
    "answer_preview": "Learners are struggling with backpropagation because…",
    "confidence": 0.74,
    "status": "pending_review",
    "created_at": "2026-08-02T14:50:37.976374"
  }
]
```

## GET /api/insights/{insight_id}

Retrieve generated output, citations, and status. Requires `insights:read`.

## GET /api/segments/{segment_id}

Retrieve one segment's content — used to preview what a citation actually says (e.g. the real transcript text or slide OCR) instead of showing a bare, opaque `segment_id`. Gated on the same `insights:read` permission as viewing the insight that cites it.

```json
{
  "segment_id": "uuid",
  "asset_id": "uuid",
  "modality": "discussion",
  "text_content": "...",
  "timestamp_start": null,
  "timestamp_end": null
}
```

## POST /api/review-feedback

Store accept, edit, reject, or escalate decisions on a generated insight. Requires `review:write` (the one permission `educator` does **not** have — a `reviewer` or `admin` role is required).

```json
// Request
{ "insight_id": "uuid", "decision": "accept", "notes": "Matches what we saw in support tickets." }
// Response
{ "feedback_id": "uuid", "insight_id": "uuid", "decision": "accept" }
```

Cited assets advance to `JobStage.reviewed` — the last automatic lifecycle stage.

## GET /api/metrics

Return pipeline health (per-stage job counts across all 9 stages), review outcomes, and coverage counts. Requires `metrics:read`.

```json
{
  "pipeline_health": { "uploaded": 15, "preprocessed": 0, "embedded": 0, "indexed": 3, "searchable": 0, "retrieved": 1, "synthesized": 0, "reviewed": 0, "archived": 0, "failed": 1 },
  "review_outcomes": { "accept": 5 },
  "total_assets": 42,
  "total_segments_indexed": 76,
  "total_jobs": 20,
  "failed_jobs": 1,
  "total_insights": 15,
  "pending_review": 10
}
```

## GET /api/audit-log

Governance-ready record of every mutating action across the platform — who did it, what it touched, and when. Requires `audit:read`.

```json
// GET /api/audit-log?limit=50
[
  {
    "id": "uuid",
    "actor": "admin-test",
    "action": "insight.review",
    "resource_type": "insight",
    "resource_id": "uuid",
    "details": { "decision": "accept", "notes": "..." },
    "created_at": "2026-08-02T14:50:37.976374"
  }
]
```
