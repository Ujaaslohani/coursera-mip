# backend

Backend API for the Coursera Multimodal Intelligence Platform. Implements the
API surface specified in the product brief §7.3 exactly:

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/assets` | Register a new video, image, slide, transcript, quiz, or discussion asset |
| POST | `/api/processing-jobs` | Start preprocessing, segmentation, extraction, and metadata normalization |
| GET | `/api/processing-jobs/{job_id}` | Retrieve job status, warnings, failures, and output records |
| POST | `/api/embeddings` | Generate or refresh embeddings for approved asset segments |
| POST | `/api/query` | Accept a unified user query and run permission-aware retrieval across modalities |
| POST | `/api/synthesize` | Generate grounded insight packs from retrieved evidence |
| GET | `/api/insights/{insight_id}` | Retrieve generated output, citations, evidence records, and status |
| POST | `/api/review-feedback` | Store accept, edit, reject, escalation, and quality-feedback actions |
| GET | `/api/metrics` | Return pipeline health, retrieval quality, review outcomes, and usage metrics |

## Structure

```
app/
  api/        # route handlers, one file per resource
  auth/       # bearer-token auth dependency, enforced on every route
  services/   # business logic per resource
  jobs/       # processing-job state machine helpers
  database/   # SQLAlchemy models + session
```

Embedding generation, retrieval ranking, and LLM synthesis logic live in the
sibling `../ai` folder and are imported in-process (see `app/services/embedding_service.py`,
`retrieval_service.py`, `synthesis_service.py`). Media preprocessing (frame
extraction, OCR, transcript alignment) lives in `../pipelines`. This repo
owns orchestration, persistence, auth, and the API contract.

## Run locally

Run from the **repo root** (one level up) with both `backend/` and the repo
root on `PYTHONPATH`, so `app.*` and `ai.*` both resolve as importable
packages:

```bash
pip install -r backend/requirements.txt -r ai/requirements.txt
cp backend/.env.example backend/.env   # fill in DATABASE_URL and OPENAI_API_KEY

# macOS/Linux (PYTHONPATH separator is :)
PYTHONPATH=.:./backend uvicorn app.main:app --reload

# Windows (PYTHONPATH separator is ;)
# PowerShell: $env:PYTHONPATH=".;./backend"; uvicorn app.main:app --reload
# Git Bash:   PYTHONPATH=".;./backend" uvicorn app.main:app --reload
```
