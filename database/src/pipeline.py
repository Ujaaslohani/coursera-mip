from pathlib import Path
import pandas as pd
from src.config import PROCESSED_DIR
from src.discovery import (discover_lecture_assets)
from src.extraction import extract_lecture_content

##savining combined project level dataframe

def save_master_dataframe(dataframe:pd.DataFrame,
                           output_path:Path) -> None:



    dataframe.to_csv(output_path, index=False, encoding='utf-8-sig')

##extracting all lectures and meatadata
def run_extraction_pipeline()->dict:

    lectures = discover_lecture_assets()

    completed_lectures = [
        lecture for lecture in lectures
        if lecture.is_complete
    ]

    if not completed_lectures:
        raise ValueError("No complete lectures found")

    ##colllecting outputs form every lecture
    video_records=[]
    caption_chunk_frames=[]
    transcript_frames=[]
    slide_manifest_frames=[]

    for index,assets in enumerate(completed_lectures,start=1):

        print(f"[{index}/{len(completed_lectures)}] extracting {assets.lecture_id}")

        result = extract_lecture_content(assets)

        video_record = (result['video_metadata'].copy())
        video_record['instructor'] = result['instructor']
        video_records.append(video_record)

        caption_chunk_frames.append(result['caption_chunk_df'])
        transcript_frames.append(result['transcript_df'])
        
        ##combiniing slide text and image metadata

        lecture_slide_manifest = result['slide_df'].merge(
            result['slide_image_df'],
            on=['lecture_id','slide_no'],
            how='inner',
            validate='one_to_one',
        )

        slide_manifest_frames.append(lecture_slide_manifest)

        print(f"{assets.lecture_id} extraction  completed")

    ##creating master dataframe
    master_video_df = pd.DataFrame(video_records)

    master_caption_chunk_df = pd.concat(caption_chunk_frames,ignore_index=True)

    master_transcript_df = pd.concat(transcript_frames,ignore_index=True)

    master_slide_manifest_df = pd.concat(slide_manifest_frames,ignore_index=True)


    ##project level outpur directory
    master_output_dir = PROCESSED_DIR / "master"

    master_output_dir.mkdir(exist_ok=True)

    ##saving only combined metadata
    save_master_dataframe(master_video_df,master_output_dir / "video_metadata.csv")
    save_master_dataframe(master_caption_chunk_df,master_output_dir / "caption_chunks.csv")
    save_master_dataframe(master_transcript_df,master_output_dir / "transcripts.csv")
    save_master_dataframe(master_slide_manifest_df,master_output_dir / "slide_manifest.csv")

    print('EXTRACTION COMPLETED')

    print("lectures:",len(master_video_df))
    print("caption chunks:",len(master_caption_chunk_df))
    print("transcript pages:",len(master_transcript_df))
    print("slides:",len(master_slide_manifest_df))
    print('master output dir:',master_output_dir)

    return {
        'video_df':master_video_df,
        'caption_chunk_df':master_caption_chunk_df,
        'transcript_df':master_transcript_df,
        'slide_manifest_df':master_slide_manifest_df,
        'master_output_dir':master_output_dir,
    }

if __name__ == "__main__":
    run_extraction_pipeline()