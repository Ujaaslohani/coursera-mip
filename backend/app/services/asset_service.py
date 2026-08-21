from sqlalchemy.orm import Session

from app.database.models import Asset, ProcessingJob
from app.jobs.job_queue import create_job


def find_duplicate(db: Session, owner: str, modality: str, storage_url: str) -> Asset | None:
    """Same owner + modality + storage_url is treated as a re-registration of
    the same source, per doc §5.4 'Input validation must detect ... duplicate
    assets.' Deliberately narrow (not fuzzy-matching content) to avoid false
    positives across genuinely different assets that happen to share a topic.
    """
    return (
        db.query(Asset)
        .filter(Asset.owner == owner, Asset.modality == modality, Asset.storage_url == storage_url)
        .first()
    )


def register_asset(db: Session, modality: str, owner: str, topic: str | None,
                    concept_tags: list[str], storage_url: str,
                    permission_scope: list[str]) -> tuple[Asset, str, bool]:
    """Returns (asset, job_id, is_duplicate)."""
    existing = find_duplicate(db, owner, modality, storage_url)
    if existing is not None:
        latest_job = (
            db.query(ProcessingJob)
            .filter(ProcessingJob.asset_id == existing.id)
            .order_by(ProcessingJob.created_at.desc())
            .first()
        )
        return existing, (latest_job.id if latest_job else create_job(db, existing.id).id), True

    asset = Asset(
        modality=modality,
        owner=owner,
        topic=topic,
        concept_tags=concept_tags,
        storage_url=storage_url,
        permission_scope=permission_scope,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    job = create_job(db, asset.id)
    return asset, job.id, False


def list_assets_with_status(db: Session, limit: int = 200) -> list[dict]:
    """Every asset with its most recent job's stage — backs the Processing
    Monitor's "what's left to process" list. A plain Python group-by (not a
    SQL window function) since asset volume here is small and this keeps the
    query trivially easy to reason about."""
    assets = db.query(Asset).order_by(Asset.created_at.desc()).limit(limit).all()
    asset_ids = [a.id for a in assets]

    latest_job_by_asset: dict[str, ProcessingJob] = {}
    if asset_ids:
        jobs = (
            db.query(ProcessingJob)
            .filter(ProcessingJob.asset_id.in_(asset_ids))
            .order_by(ProcessingJob.created_at.desc())
            .all()
        )
        for job in jobs:
            latest_job_by_asset.setdefault(job.asset_id, job)

    result = []
    for asset in assets:
        job = latest_job_by_asset.get(asset.id)
        result.append({
            "asset_id": asset.id,
            "modality": asset.modality.value,
            "owner": asset.owner,
            "topic": asset.topic,
            "job_id": job.id if job else None,
            "stage": job.stage.value if job else None,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
        })
    return result
