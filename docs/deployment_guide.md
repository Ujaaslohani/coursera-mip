# Deployment Guide

See `deployment/` for the per-target notes this summarizes.

**Live deployment:** backend on Render, frontend on Netlify.

- Backend: https://coursera-multimodal-intelligence-platform.onrender.com
- Frontend: https://courseramip.netlify.app

## Backend (Render, Docker)

The backend needs `ffmpeg` and `tesseract-ocr` — system binaries, not pip
packages — which Render's default native Python runtime doesn't provide. It's
deployed as a **Docker** web service using `backend/Dockerfile` instead.

1. Provision Postgres with the `pgvector` extension enabled (Supabase does this by default).
2. On Render: New → Web Service → connect the repo → environment **Docker**.
3. **Build context / root directory must be the repo root**, not `backend/` —
   the Dockerfile does `COPY backend/requirements.txt`, `COPY ai/requirements.txt`,
   etc. from the repo root, and the app imports `ai/` and `pipelines/` as
   top-level packages (`PYTHONPATH=/app:/app/backend`, set inside the Dockerfile).
4. Set environment variables: `DATABASE_URL`, `OPENAI_API_KEY`, `JWT_SECRET`,
   `CORS_ALLOWED_ORIGINS` (the deployed frontend origin, e.g.
   `https://courseramip.netlify.app`).
5. Render builds the image (installing `ffmpeg`/`tesseract-ocr` via
   `apt-get` as part of the build — see `backend/Dockerfile`) and runs the
   container's `CMD`, which starts uvicorn on `$PORT`.
6. Verified locally first by building and running the image with `docker build`
   / `docker run` before trusting the Render build — confirms the same image
   Render builds actually boots and serves `/health`.

Render's free tier spins the service down after inactivity; the first
request after idling is slow (cold start). Separately, the service can also
get **OOM-killed** — the free tier's memory limit (512MB) is tight for a
process that loads a local CLIP model (`sentence-transformers`) alongside
FastAPI/SQLAlchemy — which briefly shows up as a `502` with
`x-render-routing: no-deploy` until Render restarts the instance. If the
live demo looks broken (stat tiles stuck on `—`, queries failing with
"Failed to fetch"), check Render's metrics/logs for an OOM event before
assuming it's a code bug.

## Frontend (Netlify)

1. Deploy `frontend/` to Netlify, base directory `frontend/`.
2. Set `NEXT_PUBLIC_BACKEND_URL` (and `NEXT_PUBLIC_BACKEND_TOKEN`, the demo
   auth token) as Netlify environment variables.
3. **Netlify's dashboard auto-detection of the Next.js Runtime plugin can
   silently fail to attach** even when it reports the framework as "Next.js"
   — the symptom is every route 404ing despite a "successful" build, with the
   build log showing `0 new function(s) to upload`. Fixed with an explicit
   `frontend/netlify.toml`:
   ```toml
   [build]
     command = "npm run build"
     publish = ".next"
   [[plugins]]
     package = "@netlify/plugin-nextjs"
   ```
   See `deployment/netlify_notes.md` for the full story.

## Media pipelines

`pipelines/` requires system binaries (`ffmpeg`, `tesseract-ocr`) not
available on typical serverless platforms — this is exactly why the backend
runs as a Docker container (see above) rather than on a native/serverless
Python runtime. Preprocessing jobs run in-process on the same container as
the API.

## Known limitations of the current deployment

- **Exposed admin token:** the frontend authenticates with a long-lived JWT
  passed via `NEXT_PUBLIC_BACKEND_TOKEN`, which Next.js inlines into the
  public client JS bundle at build time — anyone can read it out of the
  deployed site's JS. Acceptable for a demo with no real user data; would
  need a real login flow (or a much more tightly scoped, short-lived token)
  before going further.
- **Render free tier reliability:** cold starts are expected, and the
  instance can get OOM-killed under the free tier's 512MB memory limit
  (largely from holding a local CLIP model in memory) — shows up as a
  transient `502 no active deployment` until Render restarts it, not a
  backend bug. Upgrading the Render plan (more memory) or moving CLIP
  inference to a lighter/separate process would remove this.

## Verifying a deployment

1. `GET /health` on the backend returns `{"status": "ok"}`.
2. Seed `data/sample_assets/assets_manifest.json` via `/api/assets`.
3. Run one query from `data/sample_queries.json` through `/api/query` + `/api/synthesize`.
4. Confirm the frontend Query Workspace renders the cited answer.
5. Open the deployed frontend URL directly and check the browser console for
   CORS or fetch errors — confirms `CORS_ALLOWED_ORIGINS` on the backend
   actually matches the frontend's origin.
