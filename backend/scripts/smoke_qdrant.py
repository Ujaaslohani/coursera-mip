from pathlib import Path
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from app.config import get_settings  # noqa: E402
from app.services.qdrant_service import QdrantService  # noqa: E402


def main() -> None:
    settings = get_settings()
    service = QdrantService(settings)

    collection = service.get_collection()
    print(f"collection={collection.collection_name}")
    print(f"status={collection.status}")
    print(f"points_count={collection.points_count}")

    sample = service.scroll_records(limit=3)
    print(f"sample_records={len(sample.records)}")
    for record in sample.records:
        print(f"- id={record.id} payload_keys={sorted(record.payload.keys())[:8]}")


if __name__ == "__main__":
    main()
