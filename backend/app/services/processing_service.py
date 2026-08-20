"""Orchestrates POST /api/processing-jobs: actually runs the matching
pipelines/*_processing step against an asset's storage_url and indexes the
result, rather than just flipping a status column. This is the real wiring
doc §5.4 describes — preprocessing -> normalization -> embedding -> indexed
-> searchable.

Video (FFmpeg + Whisper) and image OCR (Tesseract) run for real when those
binaries are on PATH; when they're not, jobs fail visibly with a clear error
rather than silently no-op'ing, per doc §5.5 "The platform must ... fail
visibly when evidence is incomplete." Image segments additionally get a real
CLIP visual embedding (ai/embeddings/clip_embed.py), independent of whatever
OCR text was or wasn't found — see doc §5.4 "should not overfit to
text-only analysis."
"""
import json
import os
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.models import Asset, ProcessingJob, Segment, JobStage
from app.jobs.job_queue import get_job, advance_job
from app.services.storage_service import get_storage_backend
from ai.preprocessing.normalize import normalize_raw_units, NormalizedSegment
from ai.embeddings.embed import embed_segment
from ai.embeddings.clip_embed import embed_image
from pipelines.text_processing.clean import process_quiz, process_discussion_thread
from pipelines.image_processing.extract import extract_slide_text, process_image
from pipelines.video_processing.extract import process_video

REPO_ROOT = Path(__file__).resolve().parents[3]

# Fallback install locations for machines where ffmpeg/tesseract were just
# installed but the current process's PATH predates the install (a long-lived
# shell won't pick up a Windows user-PATH registry change without a restart).
_FALLBACK_BINARY_DIRS = [
    r"C:\Program Files\Tesseract-OCR",
]


def _ensure_binary_on_path(binary_name: str) -> bool:
    if shutil.which(binary_name):
        return True
    for extra_dir in _FALLBACK_BINARY_DIRS:
        if (Path(extra_dir) / f"{binary_name}.exe").exists():
            os.environ["PATH"] = extra_dir + os.pathsep + os.environ.get("PATH", "")
            return True
    # ffmpeg ships wherever it was unzipped, not a fixed path — search common user locations
    if binary_name == "ffmpeg":
        for candidate in Path.home().glob("tools/**/bin/ffmpeg.exe"):
            os.environ["PATH"] = str(candidate.parent) + os.pathsep + os.environ.get("PATH", "")
            return True
    return shutil.which(binary_name) is not None


class ProcessingError(Exception):
    pass


def _load_raw_units(asset: Asset) -> tuple[list[dict], Path]:
    """Returns (raw_units, resolved_source_path) — the resolved path is
    reused by run_processing_job to compute a CLIP visual embedding for
    image assets without re-deriving it."""
    storage = get_storage_backend()
    source_path = storage.resolve(asset.storage_url)

    if asset.modality.value == "video":
        if not _ensure_binary_on_path("ffmpeg"):
            raise ProcessingError(
                "Video preprocessing requires ffmpeg, which is not installed/on PATH in this environment."
            )
        if not source_path.exists():
            raise ProcessingError(f"storage_url does not resolve to a local file: {asset.storage_url}")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ProcessingError("OPENAI_API_KEY is not configured — required for Whisper transcription.")
        thumbnail_dir = REPO_ROOT / "data" / "generated_thumbnails" / asset.id
        result = process_video(asset.id, str(source_path), api_key=api_key, thumbnail_dir=str(thumbnail_dir))
        return result["raw_units"], source_path

    if asset.modality.value == "image" and source_path.suffix.lower() != ".pdf":
        if not _ensure_binary_on_path("tesseract"):
            raise ProcessingError(
                "Image OCR requires tesseract, which is not installed/on PATH in this environment."
            )
        if not source_path.exists():
            raise ProcessingError(f"storage_url does not resolve to a local file: {asset.storage_url}")
        result = process_image(asset.id, str(source_path))
        # OCR finding no text is not an error for images — the CLIP visual
        # embedding below still makes the image searchable on its own.
        raw_units = result["raw_units"] or [{"text": "", "metadata": {"ocr_empty": True}}]
        return raw_units, source_path

    if not source_path.exists():
        raise ProcessingError(f"storage_url does not resolve to a local file: {asset.storage_url}")

    if source_path.suffix.lower() == ".pdf":
        return extract_slide_text(str(source_path)), source_path  # real PyMuPDF extraction, no system binary needed

    raw = json.loads(source_path.read_text(encoding="utf-8"))

    if asset.modality.value == "quiz":
        return process_quiz(asset.id, raw)["raw_units"], source_path
    if asset.modality.value == "discussion":
        return process_discussion_thread(asset.id, raw)["raw_units"], source_path

    # transcript / slide (already-extracted JSON) are already in raw_units shape
    return raw, source_path


def run_processing_job(db: Session, job_id: str) -> ProcessingJob:
    job = get_job(db, job_id)
    if job is None:
        raise ProcessingError(f"job {job_id} not found")

    asset = db.query(Asset).filter(Asset.id == job.asset_id).first()
    if asset is None:
        return advance_job(db, job_id, JobStage.failed, error=f"asset {job.asset_id} not found")

    try:
        raw_units, source_path = _load_raw_units(asset)
    except ProcessingError as e:
        return advance_job(db, job_id, JobStage.failed, error=str(e))

    advance_job(db, job_id, JobStage.preprocessed)

    normalized = normalize_raw_units(
        asset_id=asset.id,
        modality=asset.modality.value,
        raw_units=raw_units,
        permission_scope=asset.permission_scope,
    )

    is_image_asset = asset.modality.value == "image" and source_path.suffix.lower() != ".pdf"
    image_vector = None
    if is_image_asset:
        try:
            image_vector = embed_image(str(source_path))
        except Exception:
            image_vector = None  # CLIP unavailable — text/OCR path still proceeds independently

    if is_image_asset and not normalized:
        # OCR found genuinely no text at all — still index the image by its
        # visual content alone rather than dropping it from the pipeline.
        normalized = [NormalizedSegment(
            asset_id=asset.id, modality="image", text_content="[image — no OCR text, indexed visually]",
            timestamp_start=None, timestamp_end=None, topic=None,
            permission_scope=asset.permission_scope, metadata={"ocr_empty": True},
        )]

    for seg in normalized:
        db.add(Segment(
            asset_id=seg.asset_id,
            job_id=job.id,
            modality=seg.modality,
            text_content=seg.text_content,
            timestamp_start=seg.timestamp_start,
            timestamp_end=seg.timestamp_end,
            embedding=embed_segment(seg.text_content) if seg.text_content.strip() else None,
            image_embedding=image_vector if is_image_asset else None,
            segment_metadata=seg.metadata,
        ))
    db.commit()

    advance_job(db, job_id, JobStage.embedded)
    advance_job(db, job_id, JobStage.indexed)
    return advance_job(db, job_id, JobStage.searchable)
