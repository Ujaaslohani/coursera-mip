"""
EXTRACTING  
Video metadata
VTT captions
Transcript text
Slide text
Slide images  """

import json
import cv2
from collections import Counter
from pathlib import Path
import re
import fitz
import pandas as pd
import webvtt
from src.config import (CAPTION_CHUNK_SIZE,CAPTION_OVERLAP_SIZE,lecture_output_dir)

from src.discovery import LectureAssets

#------------------------------------------------------------------------------
##converting timesamp to seconds
#------------------------------------------------------------------------------

def timestamp_to_seconds(timestamp:str)->float:
    hours, minutes, seconds = map(float, timestamp.split(':'))

    return ((hours )* 3600 + (minutes)*60 + seconds)

# ------------------------------------------------------------
##EXTRACTING VIDEO METADATA
#------------------------------------------------------------------------------

def extract_video_metadata(lecture_id:str,
                           video_path:Path,
                           output_dir:Path)->dict:

    video= cv2.VideoCapture(str(video_path)) ##opening and processing lec02 video

    if not video.isOpened():
        video.release()
        raise ValueError(f"Could not open the Video {video_path}")
    else:
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) ##total no of frames
        fps=int(video.get(cv2.CAP_PROP_FPS))  ##no of frames per second
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)) ##width of the frame
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) ##height of the frame
        duration_sec = frame_count/fps if fps>0 else 0  ##duration of the video

    video.release()

    metadata = {
        "lecture_id": lecture_id,
        "video_path": str(video_path),
        "video_filename": video_path.name,
        "frame_count": frame_count,
        "fps": round(fps, 2),
        "width": width,
        "height": height,
        "duration_sec": round(duration_sec, 3),
        "file_size_bytes": video_path.stat().st_size,
    } 

    ##saving the metadata to a json file
    output_path = output_dir / f"{lecture_id}_video_metadata.json"

    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return metadata

#----------------------------------------------------------
##EXTRACTING VTT CAPTIONS
#------------------------------------------------------------------------------

def extract_vtt_captions(lecture_id:str,
                         caption_path:Path,
                         output_dir:Path)->pd.DataFrame:

    caps = webvtt.read(str(caption_path))
    cap_rows=[]

    for cap_id,cap in enumerate(caps,start=1):

        cap_text = " ".join(cap.text.strip().split())

        if not cap_text:
            continue

        start_seconds = timestamp_to_seconds(cap.start)
        end_seconds = timestamp_to_seconds(cap.end) 

          ##appending to list
        cap_rows.append({
            'lecture_id':lecture_id,
            'caption_id':cap_id,
            'start_time':cap.start,
            'end_time':cap.end,
            'text':cap_text,
            'start_seconds':start_seconds,
            'end_seconds':end_seconds,
            'duration_seconds':end_seconds-start_seconds,
            'word_count':len(cap_text.split()),
        }) 

    ##converting to dataframe
    cap_df = pd.DataFrame(cap_rows)

    ##saving to csv
    cap_df.to_csv(output_dir / f"{lecture_id}_captions.csv", index=False, encoding='utf-8-sig')

    return cap_df

##------------------------------------------------------------------------------
## EXTRCTING INSTRUCTORS/SPEAKER NAMES FROM TRANSCIPT
#------------------------------------------------------------------------------

def extract_instructor(transcript_text: str, ) -> str:

    speaker_labels= re.findall(r"(?m)^\s*([A-Z][A-Z .'\-]{2,}):", transcript_text)

    if not speaker_labels:
        return ""

    cleaned_labels= [" ".join(label.split()) for label in speaker_labels]

    speaker_counts = Counter(cleaned_labels)
    return "; ".join(speaker for speaker,_ in speaker_counts.most_common())


#------------------------------------------------------------------------------
##EXTRACTING TRANSCRIPT TEXT
#------------------------------------------------------------------------------
def extract_tarnscript_text(lecture_id:str,
                            transcript_path:Path,
                            output_dir:Path)->tuple[pd.DataFrame,str]:

    doc =fitz.open(transcript_path) ##opening transcript document

    rows=[]

    for index,page in enumerate(doc,start=1):
        page_text =page.get_text('text').strip()

        rows.append({
            'lecture_id':lecture_id,
            'page_no':index,
            'text':page_text,
            'char_count':len(page_text),
            "word_count":len(page_text.split())
        })

    doc.close()
    transcript_df = pd.DataFrame(rows)

    full_transcript_text = "\n".join(transcript_df['text'].fillna(""))
    instructor = extract_instructor(full_transcript_text)

    transcript_df['instructor'] = instructor

    ##saving to csv
    transcript_df.to_csv(output_dir / f"{lecture_id}_transcript.csv", index=False, encoding='utf-8-sig')

    return transcript_df,instructor

#----------------------------------------------------------
##return first non_empty string
#------------------------------------------------------------------------------

def first_non_empty(text:str)->str:
    for line in text.splitlines():
        cleaned_line = line.strip()
        if cleaned_line:
            return cleaned_line
    return ""

#---------------------------------------------------------------
## EXTRACTING SLIDE TEXT
#------------------------------------------------------------------------------

def extract_slide_text(lecture_id:str,
                       slide_path:Path,
                       output_dir:Path)-> tuple[pd.DataFrame,pd.DataFrame]:

    slide_image_dir= output_dir / "slide_images"
    slide_image_dir.mkdir(exist_ok=True)

    slide_records=[]
    image_records=[]

    with fitz.open(slide_path) as doc:

        ##extracting first page and thrid page
        ##for lecture-level title/topic metadata

        first_page_text = (doc[0].get_text('text').strip() if len(doc)>0 else "")
        third_page_text = (doc[2].get_text('text').strip() if len(doc)>2 else "")

        lecture_title = first_non_empty(first_page_text)
        lecture_topic = first_non_empty(third_page_text)

        for slide_no,slide in enumerate(doc,start=1):

            text = slide.get_text('text').strip()
            word_count = len(text.split())

            slide_records.append({
                'lecture_id':lecture_id,
                'slide_no':slide_no,
                'text':text,
                'char_count':len(text),
                'word_count':word_count,
                'lecture_title':lecture_title,
                'lecture_topic':lecture_topic,
                'visual_processing_needed':(word_count<100),
            })

            image_file_name = f"{lecture_id}_slide_{slide_no:03d}.png"
            image_path = slide_image_dir / image_file_name

            ##avoiding saving duplicate images
            if image_path.exists():

                image = cv2.imread(str(image_path))

                if image is None:
                    raise FileNotFoundError(f"Could not read image {image_path}")

                image_height, image_width= image.shape[:2]

            else:
                pixmap = slide.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)

                pixmap.save(str(image_path))

                image_width, image_height = pixmap.width, pixmap.height

            image_records.append({
                'lecture_id':lecture_id,
                'slide_no':slide_no,
                'image_file_name':image_file_name,
                'image_file_path':str(image_path),
                'image_width':image_width,
                'image_height':image_height,
                'image_size_bytes':image_path.stat().st_size,
            })

    ##creating dataframes

    slide_df = pd.DataFrame(slide_records)

    slide_image_df = pd.DataFrame(image_records)

    slide_df.to_csv(output_dir / f"{lecture_id}_slides.csv", index=False, encoding='utf-8-sig')
    slide_image_df.to_csv(output_dir / f"{lecture_id}_slide_images.csv", index=False, encoding='utf-8-sig')

    return slide_df,slide_image_df


##----`-------------------------------------------------------------------
# COMIBNE CAPITONS INTO CHUNKS
#------------------------------------------------------------------------------

def create_caption_chunks(caption_df:pd.DataFrame,
                          output_dir:Path,
                          target_words: int=CAPTION_CHUNK_SIZE,
                          overlap_words: int=CAPTION_OVERLAP_SIZE)->pd.DataFrame:

    if caption_df.empty:
        raise ValueError("caption_df is empty")

    caption_df = caption_df.sort_values(by=['caption_id']).reset_index(drop=True)

    lecture_id = caption_df.loc[0,'lecture_id']

    chunk_records=[]

    start_index = 0
    chunk_number = 1
    total_captions = len(caption_df)

    while start_index < total_captions:

        end_index = start_index 
        curr_word_count = 0

    ##finding the end of the chunk
        while (end_index < total_captions and curr_word_count < target_words):
            curr_word_count += int(caption_df.loc[end_index,'word_count'])
            end_index += 1

        ###end index is exclusive

        final_index = end_index-1

        chunk_captions = caption_df.iloc[start_index:end_index]

        chunk_text = " ".join(chunk_captions['text'].fillna("").astype(str)).strip()

        start_seconds = float(caption_df.loc[start_index,'start_seconds'])
        end_seconds = float(caption_df.loc[final_index,'end_seconds'])

        chunk_records.append({
            'chunk_id':f"{lecture_id}_caption_chunk_{chunk_number:02d}",
            'lecture_id':lecture_id,
            'start_caption_id':int(caption_df.loc[start_index,'caption_id']),
            'end_caption_id':int(caption_df.loc[final_index,'caption_id']),
            'start_time':caption_df.loc[start_index,'start_time'],
            'end_time':caption_df.loc[final_index,'end_time'],
            'text':chunk_text,
            'start_seconds':round(start_seconds,3),
            'end_seconds':round(end_seconds,3),
            'duration_seconds':round(end_seconds-start_seconds,3),
            'word_count':len(chunk_text.split()),
        })

        if end_index >= total_captions:
            break

        next_start_index = max(start_index+1,end_index-overlap_words)
        start_index = next_start_index
        chunk_number += 1

    caption_chunk_df = pd.DataFrame(chunk_records)

    caption_chunk_df.to_csv(output_dir / f"{lecture_id}_caption_chunks.csv", index=False, encoding='utf-8-sig')
    return caption_chunk_df



#----------------------------------------------------------
## RUNNING EXTRACTIONS
#------------------------------------------------------------------------------

def extract_lecture_content(
        assets:LectureAssets,) -> dict:

    if not assets.is_complete:
        raise ValueError(f"{assets.lecture_id} is not complete", {",".join(assets.missing_assets)})

    output_dir = lecture_output_dir(assets.lecture_id)/"extracted"
    output_dir.mkdir(parents=True, exist_ok=True)


    video_metadata = extract_video_metadata(assets.lecture_id,
                                            assets.video_path,
                                            output_dir)

    caption_df = extract_vtt_captions(assets.lecture_id,
                                      assets.caption_path,
                                      output_dir)

    caption_chunk_df = create_caption_chunks(caption_df,output_dir)

    transcript_df,instructor = extract_tarnscript_text(assets.lecture_id,
                                                       assets.transcript_path,
                                                       output_dir)

    slide_df,slide_image_df = extract_slide_text(assets.lecture_id,
                                                 assets.slide_path,
                                                 output_dir)

    return {
        "video_metadata":video_metadata,
        "caption_df":caption_df,
        "caption_chunk_df":caption_chunk_df,
        "transcript_df":transcript_df,
        "instructor":instructor,
        "slide_df":slide_df,
        "slide_image_df":slide_image_df,
        "output_dir":output_dir,
    }

