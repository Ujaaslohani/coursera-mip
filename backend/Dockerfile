# Built from the REPO ROOT (not backend/) — Render build context must be set
# to the repository root, because the backend imports ai/ and pipelines/ as
# top-level packages (see PYTHONPATH below), not as backend-local modules.
#
# Local equivalent of what this replicates:
#   PYTHONPATH="..;." uvicorn app.main:app   (run from inside backend/)

FROM python:3.11-slim

# ffmpeg (video) + tesseract-ocr (image OCR) — the two system binaries that
# are NOT installable via pip and were "fail visibly" gaps on Render's
# default native runtime. This is the whole reason this Dockerfile exists.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first so dependency installs are cached across
# builds that don't touch requirements.txt.
COPY backend/requirements.txt backend/requirements.txt
COPY ai/requirements.txt ai/requirements.txt
COPY pipelines/requirements.txt pipelines/requirements.txt
RUN pip install --no-cache-dir \
    -r backend/requirements.txt \
    -r ai/requirements.txt \
    -r pipelines/requirements.txt

# Now copy the rest of the repo (ai/, pipelines/, backend/, data/ — the
# backend resolves sample asset paths relative to repo root via
# backend/app/services/storage_service.py).
COPY . .

ENV PYTHONPATH=/app:/app/backend
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
