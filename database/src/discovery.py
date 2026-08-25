"""This module scans the four raw-data folders and matches each video, caption, transcript, and slide PDF by lecture number.
 It automatically discovers available lectures,  missing lec22 is simply absent."""

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

## import config

from src.config import(
    CAPTION_DIR,
    SLIDE_DIR,
    TRANSCRIPT_DIR,
    VIDEO_DIR,
    MANIFEST_DIR,
    normalize_lecture_id,)

#------------------------------------------------------------------------------
##RAW FILES BELONG TO A LECTURE, EACH LECTURE IS IDENTIFIED BY LECTURE_ID
#------------------------------------------------------------------------------

@dataclass(frozen=True)
class LectureAssets:
    lecture_id: str
    caption_path: Optional[Path]
    slide_path: Optional[Path]
    video_path: Optional[Path]
    transcript_path: Optional[Path]

    @property
    def is_complete(self)->bool:
        """checking if all assets are available
        and return trure if all four assetse exist"""

        return all((self.video_path,
                    self.slide_path,
                    self.caption_path,
                    self.transcript_path))

    ##if assets are missing,return the names of missing assets
    @property
    def missing_assets(self) -> list[str]:
        assets={
            'video': self.video_path,
            'slide': self.slide_path,
            'caption': self.caption_path,
            'transcript': self.transcript_path
        }
        return [name for name, path in assets.items() if not path]


#------------------------------------------------------------------------------
##extracting the normalized lecture ids from filename
#------------------------------------------------------------------------------


def extract_lecture_id(file_path:Path) -> Optional[str]:

    matched = re.search(r"(?:lecture|lec)[_\-\s]*0*(\d+)",
                        file_path.stem,
                        flags=re.IGNORECASE)

    if not matched:
        return None

    return normalize_lecture_id(f"lec{matched.group(1)}")

#------------------------------------------------------------------------------
# indexing assets
#------------------------------------------------------------------------------ 

def index_assets(directory:Path,extensions:set[str],) -> dict[str,Path]:

    """indexing files in one asset directory by lecture_id """
    asset_index: dict[str,Path] = {}

    for file_path in directory.rglob("*"):

        if (not file_path.is_file() or file_path.suffix.lower() not in extensions):
            continue

        lecture_id = extract_lecture_id(file_path)

        if not lecture_id:
            continue

        if lecture_id in asset_index:
            raise ValueError(f"Duplicate lecture_id {lecture_id} found in {file_path} and {asset_index[lecture_id]}")

        asset_index[lecture_id] = file_path
    return asset_index

#------------------------------------------------------------------------------
# discovering lecture assets
#------------------------------------------------------------------------------

def discover_lecture_assets() -> list[LectureAssets]:

    """ discover and match asssets accross all raw_data folders. """

    videos = index_assets(VIDEO_DIR, {".mp4", ".mkv", ".avi"})
    captions = index_assets(CAPTION_DIR, {".vtt", ".srt"})
    transcripts = index_assets(TRANSCRIPT_DIR, {".pdf"})
    slides = index_assets(SLIDE_DIR, {".pdf"})

    ##including lecturew with partial missing assets.
    lecture_ids = sorted(
        set(videos)
        |set(captions)
        |set(transcripts)
        |set(slides),
        key=lambda value: int(re.search(r"\d+", value).group()),
    )


    return [LectureAssets(
        lecture_id=lecture_id,
        caption_path=captions.get(lecture_id),
        slide_path=slides.get(lecture_id),
        video_path=videos.get(lecture_id),
        transcript_path=transcripts.get(lecture_id),
    ) for lecture_id in lecture_ids]

#------------------------------------------------------------------------------
# saving lecture asset inventory
#------------------------------------------------------------------------------

def save_asset_inventory(lectures:list[LectureAssets]) -> Path:

    """saving one consice invenory of discovered lecture assets """

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    output_path = MANIFEST_DIR / "lecture_assets_inventory.csv"

    feilds =['lecture_id', 'video_path', 'slide_path', 'caption_path', 'transcript_path', 'status', 'missing_assets']

    with open(output_path,'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=feilds)
        writer.writeheader()

        for lecture in lectures:
            writer.writerow({
                'lecture_id': lecture.lecture_id,
                'video_path': str(lecture.video_path) if lecture.video_path else '',
                'slide_path': str(lecture.slide_path) if lecture.slide_path else '',
                'caption_path': str(lecture.caption_path) if lecture.caption_path else '',
                'transcript_path': str(lecture.transcript_path) if lecture.transcript_path else '',
                'status': 'complete' if lecture.is_complete else 'incomplete',
                'missing_assets': ', '.join(lecture.missing_assets),
            })
    return output_path



if __name__ == "__main__":
    discovered_lectures = discover_lecture_assets()
    inventory_path = save_asset_inventory(discovered_lectures)

    complete_count = sum(lecture.is_complete for lecture in discovered_lectures)
    
    print(f'lectures discovered: {len(discovered_lectures)}')
    print(f'complete lectures: {complete_count}')

    print('inventory saved to:', inventory_path)

