##BUILDING STRUCTURED DATABASES FROM EXTRACTED LECTURE METADATA
import json
from pathlib import Path
import pandas as pd
from src.config import PROCESSED_DIR,COURSE_ID

CAPTION_SEGMENT_DIR = PROCESSED_DIR
DATABASE_DIR = PROCESSED_DIR / "databases"


##LOADING ALL CAPTION CHUNKS AND COMBINE ALL CHUNKS FROM ALL LECTURES

def load_all_caption_chunks() -> pd.DataFrame:

    caption_files = sorted(CAPTION_SEGMENT_DIR.rglob("lec*/extracted/*caption_chunks.csv"))


    if not caption_files:
        raise FileNotFoundError(f"No caption files found in {CAPTION_SEGMENT_DIR}")

    caption_frame=[]

    for cap_file in caption_files:
        cap_df = pd.read_csv(cap_file)
        caption_frame.append(cap_df)

    return pd.concat(caption_frame,ignore_index=True)


##BUILDING CAPTION DATABASE
def build_caption_database() ->pd.DataFrame:

    caption_df = load_all_caption_chunks()

    lecture_numbers = caption_df['lecture_id'].str.extract(r"(\d+)",expand=False).astype(int)

    caption_df['asset_id'] = lecture_numbers.map(lambda number: f"VIDEO_LEC{number:02d}")

    caption_df['course_id'] = COURSE_ID
    caption_df['module_id'] = lecture_numbers.map(lambda number: f"MOD_{number:02d}")


    ##using chunk_id as the unique identifier for caption records

    caption_df['record_id'] = caption_df['chunk_id']

    ##for source identification when records enter the vector database
    caption_df['content_type'] = 'caption'

    ##necessary records for retreival and citations

    required_columns=[
        'record_id',
        'chunk_id',
        'asset_id',
        'course_id',
        'module_id',
        'lecture_id',
        'start_caption_id',
        'end_caption_id',
        'start_time',
        'end_time',
        'start_seconds',
        'end_seconds',
        'text',
        'word_count',
        'duration_seconds',
        'content_type',
    ]

    missing_columns = [column for column in required_columns if column not in caption_df.columns]


    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    caption_database_df = caption_df[required_columns].copy()

    ##sort records into lecture and timestamp order
    caption_database_df = caption_database_df.sort_values(by=['lecture_id','start_seconds']).reset_index(drop=True)

    return caption_database_df

##saving caption database
def save_caption_database(caption_database_df:pd.DataFrame)->tuple[Path,Path]:

    ##saving caption database as a csv and json

    DATABASE_DIR .mkdir(parents=True, exist_ok=True)

    csv_path = DATABASE_DIR / "caption_database.csv"
    json_path = DATABASE_DIR / "caption_database.json"


    caption_database_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    records = caption_database_df.where(pd.notna(caption_database_df),None).to_dict(orient='records')

    with open(json_path, "w", encoding='utf-8') as file:
        json.dump(records,file,ensure_ascii=False,indent=2)

    return csv_path,json_path

if __name__ == "__main__":
    caption_database = build_caption_database()

    csv_output_path,json_output_path = save_caption_database(caption_database)

    ## one consice validation
    print('caption database completed')
    print('caption records:',len(caption_database))
    print('duplicate record count:',caption_database.duplicated(subset=['record_id']).sum())
    print('csv output path:',csv_output_path)
    print('json output path:',json_output_path)
