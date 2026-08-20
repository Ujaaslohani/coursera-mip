# Architecture

## Workflow

```
Input (video/image/slide/transcript/quiz/discussion)
  -> Preprocessing (pipelines/)
  -> Embeddings — text (ai/embeddings/embed.py) + visual/CLIP (ai/embeddings/clip_embed.py)
  -> Unified Query (backend/app/api/query.py)
  -> Retrieval Planner agent (ai/agents/retrieval_planner.py) decides search strategy
  -> Retrieval (ai/retrieval/, permission-aware, dual text+visual pgvector search)
  -> Evidence Ranker agent (ai/agents/evidence_ranker.py) re-orders for cross-modal diversity
  -> LLM Synthesis (ai/synthesis/, cited + grounded)
  -> Quality Validator agent (ai/agents/quality_validator.py) strips unsupported citations
  -> Human Review (backend/app/api/review_feedback.py)
```

This matches the product brief's required workflow, extended past its v1 simplification — see "Second-pass upgrades" below.

## Repo-to-layer mapping

| Doc layer (§6.2) | Repo folder |
|---|---|
| Frontend/Product Layer | `frontend/` |
| Backend/API Layer | `backend/` |
| AI Workflow Layer | `ai/` (includes `ai/agents/` — the agent pipeline) |
| Media Processing | `pipelines/` |
| Multimodal Data Layer | Postgres + pgvector, managed via `backend/app/database/` |
| Object Storage | `backend/app/services/storage_service.py` — local filesystem by default, S3-compatible when `OBJECT_STORAGE_URL`/`OBJECT_STORAGE_KEY` are set |
| Governance | RBAC (`backend/app/auth/dependencies.py`) + audit log (`backend/app/services/audit_service.py`, `backend/app/api/audit_log.py`) |

## Data flow detail

1. `POST /api/assets` registers an asset (after a duplicate check) and creates a `ProcessingJob` in stage `uploaded`.
2. `POST /api/processing-jobs` resolves the file via the storage abstraction, runs the matching `pipelines/*_processing` step, normalizes the output (`ai/preprocessing`), embeds it — text via OpenAI, plus a real CLIP visual embedding for images (`ai/embeddings/clip_embed.py`) — and writes `Segment` rows stamped with the job's ID. The job advances through `preprocessed → embedded → indexed → searchable`.
3. `POST /api/query` runs the Retrieval Planner agent first (decides search terms + how many results), then `ai/retrieval/retriever.py` runs **two independent searches** — text-meaning (OpenAI embeddings) and visual-meaning (CLIP) — merges them, then the Evidence Ranker agent re-orders for cross-modal diversity before the `top_k` cut. Every asset behind a retrieved segment advances to `retrieved`.
4. `POST /api/synthesize` passes only the retrieved, permitted evidence to the LLM (`ai/synthesis/`), which must cite every claim. The Quality Validator agent then strips any citation that doesn't map to retrieved evidence and caps confidence if it had to. Cited assets advance to `synthesized`.
5. `POST /api/review-feedback` records a human decision (accept/edit/reject/escalate) before an insight is treated as approved; cited assets advance to `reviewed`. `POST /api/processing-jobs/{id}/archive` is the final, manual stage.
6. Every mutating call above also writes to `audit_log` via `backend/app/services/audit_service.py`, and every route is gated by a role→permission check (`require_role_permission()` in `backend/app/auth/dependencies.py`) — not just authentication.

## Design principle

Every `Segment` retains `asset_id`, `job_id`, `modality`, and `timestamp_start/end`, so
every citation in a synthesized insight can be traced back to its exact
source — required by doc §5.4 and graded under "Evidence Traceability" (§3).
`job_id` specifically is what lets lifecycle-stage advancement (`retrieved`/`synthesized`/`reviewed`) attach to the correct processing run when an asset has been re-processed more than once.

## Second-pass upgrades (beyond the v1 simplification)

The first working version of this platform (see `docs/platform_flow_walkthrough.md` §1–§6) deliberately simplified four things to get an end-to-end pipeline running. All four were since built out to match the original product brief:

- **Agentic orchestration** — `ai/agents/` (planner, ranker, validator) replaced a single direct `retrieve()` → `synthesize()` call chain.
- **Real visual embeddings** — `ai/embeddings/clip_embed.py` (local CLIP ViT-B/32) replaced the OCR-text-only approximation for images. `Segment.image_embedding` (pgvector, 512-dim) is separate from the text `embedding` column (1536-dim).
- **Full 9-stage lifecycle** — `JobStage` now has all 9 values from doc §4 (`uploaded → … → reviewed → archived`), tracked per-job via `Segment.job_id`, not per-asset.
- **RBAC + audit log** — see Governance row above.

Full verification detail (real API calls, real responses, bugs found and fixed) is in `docs/platform_flow_walkthrough.md` §7.

## Non-goals for v1 — now resolved or scoped down further

- ~~Raw pixel/CLIP-style image embeddings~~ — **now implemented**, see above.
- Multi-service deployment (single FastAPI backend + single Next.js frontend, not microservices) — still true.
- Automated job workers/queues (jobs are tracked via a `ProcessingJob.stage` column, invoked synchronously) — still true.
- Real cloud object storage — the abstraction exists (`storage_service.py`) but only its local-filesystem backend is actually exercised; no `OBJECT_STORAGE_URL`/`KEY` are configured in this environment.
