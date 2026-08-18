import re
from pathlib import Path
import pandas as pd
import cv2
from src.config import (
    COURSE_ID,
    PROCESSED_DIR,
    generate_lecture_id,
    lecture_output_dir,
)

##extracting one midpoint frame from a video per every chunk_id

def extract_lecture_frame(lecture_id:str,
                          video_path:Path,
                          caption_chunk_df:pd.DataFrame,)->pd.DataFrame:

    frame_output_dir = lecture_output_dir(lecture_id) / "frame_audit"/'caption_linked_frames'

    frame_output_dir.mkdir(parents=True, exist_ok=True)

    video_capture = cv2.VideoCapture(str(video_path))

    if not video_capture.isOpened():
        video_capture.release()
        raise ValueError(f"Could not open video {video_path}")

    lecture_ids = generate_lecture_id(lecture_id)

    frame_records=[]

    for _,segment in (caption_chunk_df.sort_values(by=['start_seconds'])
                      .iterrows()):
        chunk_id = segment['chunk_id']

        ##numeric _chunk_suffixes
        chunk_match = re.search(r"(\d+)$", chunk_id)

        if not chunk_match:
            raise ValueError(f"Could not extract chunk number from {chunk_id}")

        chunk_number = int(chunk_match.group(1))

        ##midpoint of the chunk
        timestamp_seconds = round(
            (float(segment['start_seconds']) +
             float(segment['end_seconds']))/2,3)
        
        lecture_number = int(
                re.search(r"\d+",lecture_id).group())

        frame_id = (
            f"FRAME_LEC{lecture_number:02d}_"
            f"{chunk_number:03d}")

        frame_filename = (f"{frame_id.lower()}.jpg")

        frame_file_path = (frame_output_dir / frame_filename)

        ##reuse existing frame if it exists
        if frame_file_path.exists():

            frame = cv2.imread(str(frame_file_path))

            frame_read_success = (frame is not None)

        else:

            video_capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_seconds*1000)

            frame_read_success, frame = video_capture.read()

            if frame_read_success:
                frame_read_success = cv2.imwrite(str(frame_file_path), frame)

        if not frame_read_success:

            frame_records.append({
                'frame_id':frame_id,
                'asset_id':lecture_ids['video_asset_id'],
                'course_id':COURSE_ID,
                'module_id':lecture_ids['module_id'],
                'lecture_id':lecture_ids['lecture_id'],
                "primary_chunk_id":chunk_id,
                'timestamp_seconds':timestamp_seconds,
                'start_seconds':segment['start_seconds'],
                'end_seconds':segment['end_seconds'],
                'frame_filename':frame_filename,
                'frame_file_path':str(frame_file_path),
                'frame_width':None,
                'frame_height':None,
                'frame_size_bytes':None,
                 "extraction_status":"incomplete",})
            continue

        frame_records.append({
            'frame_id':frame_id,
            'asset_id':lecture_ids['video_asset_id'],
            'course_id':COURSE_ID,
            'module_id':lecture_ids['module_id'],
            'lecture_id':lecture_ids['lecture_id'],
            "primary_chunk_id":chunk_id,
            'timestamp_seconds':timestamp_seconds,
            'start_seconds':segment['start_seconds'],
            'end_seconds':segment['end_seconds'],
            'frame_filename':frame_filename,
            'frame_file_path':str(frame_file_path),
            'frame_width':frame.shape[1],
            'frame_height':frame.shape[0],
            'frame_size_bytes':frame_file_path.stat().st_size,
            "extraction_status":"complete",})

    video_capture.release()

    lecture_frame_df = pd.DataFrame(frame_records)

    lecture_frame_df.to_csv(frame_output_dir / "lecture_frames.csv", index=False, encoding='utf-8-sig')

    return lecture_frame_df


###run the function for caption linked frame extraction

def run_caption_linked_frame_extraction()-> pd.DataFrame:
    """extracts one frame per caption chunk for all videos"""

    master_dir = PROCESSED_DIR / "master"

    caption_chunk_df = pd.read_csv(master_dir / "caption_chunks.csv")

    video_metadata_df = pd.read_csv(master_dir / "video_metadata.csv")

    video_path_lookup = dict(zip(video_metadata_df['lecture_id'],
                            video_metadata_df['video_path']))

    lecture_frame_records=[]

    lecture_ids = sorted(caption_chunk_df['lecture_id'].unique(), key=lambda value: int(re.search(r"\d+", value).group()))

    for index,lecture_id in enumerate(lecture_ids,start=1):

        print(f"[{index}/{len(lecture_ids)}] Extracting {lecture_id} frame")

        lecture_chunks = caption_chunk_df[caption_chunk_df['lecture_id']==lecture_id].copy()

        video_path = video_path_lookup[lecture_id]

        lecture_frame_df = extract_lecture_frame(lecture_id,video_path,lecture_chunks)

        lecture_frame_records.append(lecture_frame_df) 

        completed_count= (lecture_frame_df['extraction_status'].eq('complete')).sum()

        print(f"{lecture_id} extracted {completed_count}/{len(lecture_frame_df)} frames")

    master_frame_df = pd.concat(lecture_frame_records,ignore_index=True)

    master_frame_path =(
        master_dir / "caption_linked_lecture_frames_manifest.csv"

    )

    master_frame_df.to_csv(master_frame_path, index=False, encoding='utf-8-sig')

    print('FRAME EXTRACTION COMPLETED')
    print('expected frames:',len(master_frame_df))

    print('extracted frames:',master_frame_df['extraction_status'].eq('complete').sum())

    print('failed frames:',master_frame_df['extraction_status'].eq('incomplete').sum())

    print('combined manifest:',master_frame_path)

    return master_frame_df

if __name__ == "__main__":
    run_caption_linked_frame_extraction()

    
