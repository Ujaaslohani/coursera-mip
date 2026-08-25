import re
from pathlib import Path
import json
import pandas as pd
import ast
from typing import Any

from src.config import PROCESSED_DIR

MASTER_DIR = PROCESSED_DIR / "master"
DATABASE_DIR = PROCESSED_DIR / "databases"
SLIDE_MANIFEST_PATH = MASTER_DIR / "slide_manifest.csv"

FRAME_MANIFEST_PATH = MASTER_DIR / "caption_linked_lecture_frames_manifest.csv"

VISUAL_ANALYSIS_PATH = MASTER_DIR / "gemini_visual_analysis.csv"


#------------------------------------------------------------------------------
# CONVERTING CSV LISTS TO PYTHON LISTS

def normalize_list_value(value: Any)->list:

    ##if the value is a list, return it
    if isinstance(value,list):
        return value

    ##if the value is null or empty, return an empty list
    if pd.isna(value) or value=="":
        return []


    try:

        ##if the value is a string, parse it as a list
        parsed_value =  ast.literal_eval(str(value))

        if isinstance(parsed_value,list):
            return parsed_value

    except (ValueError,SyntaxError):
        pass

    return [str(value)]

#------------------------------------------------------------------------------
##combining visual and textual evidence for embedding
#------------------------------------------------------------------------------
def combine_searchable_feilds(row: pd.Series) -> str:
    searchable_fields = []

    ##text or text like feilds
    text_feilds = [
        'text',
        'extracted_text',
        'summary',
        'visual_text',
        "diagram_explanation",
        'graph_explanation',
        'visual_text_relation',
    ]

    for feild in text_feilds:

        value=row.get(feild)

        if pd.notna(value) and str(value).strip():
            searchable_fields.append(str(value).strip())

    ##list like feilds
    list_feilds = ['visual_types','key_concepts','equations']

    for feild in list_feilds:
        values = normalize_list_value(row.get(feild))

        searchable_fields.extend(str(value).strip() for value in values
                                 if str(value).strip())

    return "\n".join(searchable_fields)

#---------------------------------------------------------------------------
## adding slide records
#-----------------------------------------------------------------------------

def add_slide_record_ids(slide_manifest_df:pd.DataFrame,) -> pd.DataFrame:

    ##CREATING IDS MATCHING THE IDS USED BY VUSIAL ANALYSIS
    slide_manifest_df= slide_manifest_df.copy()

    lecture_numbers = slide_manifest_df['lecture_id'].str.extract(r"(\d+)",expand=False).astype(int)

    slide_numbers = slide_manifest_df['slide_no'].astype(int)

    ##adding these ids to the slide manifest
    slide_manifest_df['visual_record_id'] = [
        f"SLIDE_LEC{lecture_number:02d}_{slide_number:03d}"
        for lecture_number,slide_number in zip(lecture_numbers,slide_numbers)
    ]

    return slide_manifest_df

#------------------------------------------------------------------------------
#building slide database
#------------------------------------------------------------------------------

def build_slide_database(visual_analysis_df:pd.DataFrame) -> pd.DataFrame:

    ##merging slide manifest with gemini visual analysis data

    slide_manifest_df = pd.read_csv(SLIDE_MANIFEST_PATH)

    slide_manifest_df = add_slide_record_ids(slide_manifest_df)

    slide_analysis_df = visual_analysis_df[
        visual_analysis_df['source_type']=='slide'].copy()

    ##slide database dataframe

    slide_database_df = slide_manifest_df.merge(slide_analysis_df,
                                                on='visual_record_id',
                                                how='inner',
                                                suffixes = ("","_analysis"),
                                                validate="one_to_one")

    slide_database_df['record_id'] = slide_database_df['visual_record_id']

    slide_database_df['content_type'] = "slide"

    slide_database_df['searchable_text'] = slide_database_df.apply(combine_searchable_feilds,axis=1)

    return slide_database_df.sort_values(by=['lecture_id','slide_no']).reset_index(drop=True)

#------------------------------------------------------------------------------
## building frame database
#------------------------------------------------------------------------------
def build_frame_database(visual_analysis_df:pd.DataFrame) -> pd.DataFrame:

    ##merging the frame metadata with gemini visual analysis data
    frame_manifest_df = pd.read_csv(FRAME_MANIFEST_PATH)

    frame_analysis_df = visual_analysis_df[
        visual_analysis_df['source_type']=='frame'].copy()

    ##frame database dataframe
    frame_database_df = frame_manifest_df.merge(frame_analysis_df,
                                                left_on='frame_id',
                                                right_on='visual_record_id',
                                                how='inner',
                                                suffixes = ("","_analysis"),
                                                validate="one_to_one"
                                                )

    frame_database_df['record_id'] = frame_database_df['frame_id']

    frame_database_df['content_type'] = "frame"

    frame_database_df['searchable_text'] = frame_database_df.apply(combine_searchable_feilds,axis=1)


    ##kepping only those frame with instructional evidence
    frame_database_df = frame_database_df[frame_database_df['is_instructional_evidence']==True].copy()

    return frame_database_df.sort_values(by=['lecture_id','timestamp_seconds']).reset_index(drop=True)

#------------------------------------------------------------------------------
## dataframe to json
#------------------------------------------------------------------------------

def dataframe_to_json(df:pd.DataFrame,) -> list[dict]:


    clean_dataframe = df.astype(object).where(pd.notna(df),None)


    return clean_dataframe.to_dict(orient='records')

#------------------------------------------------------------------------------
##save the database in csv and json format
#------------------------------------------------------------------------------

def save_database(dataframe:pd.DataFrame,
                  database_name:str,)->tuple[Path,Path]:

    DATABASE_DIR.mkdir(parents=True,exist_ok=True)

    csv_path = DATABASE_DIR / f"{database_name}.csv"
    json_path = DATABASE_DIR / f"{database_name}.json"

    dataframe.to_csv(csv_path,index=False,encoding="utf-8-sig")

    with open(json_path,"w",encoding="utf-8") as file:
        json.dump(dataframe_to_json(dataframe),file,indent=2,ensure_ascii=False)

    return csv_path,json_path

#------------------------------------------------------------------------------
## building and saving the final slide and frame databases
#------------------------------------------------------------------------------

def build_visual__database()->None:

    if not VISUAL_ANALYSIS_PATH.exists():
        raise FileNotFoundError(f"The gemini visual analysis file {VISUAL_ANALYSIS_PATH} does not exist")

    visual_analysis_df = pd.read_csv(VISUAL_ANALYSIS_PATH)

    duplicate_count = visual_analysis_df['visual_record_id'].duplicated().sum()

    if duplicate_count:
        raise ValueError(f"There are {duplicate_count} duplicated visual records")


    slide_database_df = build_slide_database(visual_analysis_df)

    frame_database_df = build_frame_database(visual_analysis_df)

    frame_csv, frame_json = save_database(frame_database_df,"frame_database")
    slide_csv, slide_json = save_database(slide_database_df,"slide_database")


    ##simple valdiation
    print('visual database completed')
    print('slide records:',len(slide_database_df))
    print('instructional frame records:',len(frame_database_df))
    print('slide database saved to',slide_csv)
    print('frame database saved to',frame_csv)


if __name__=='__main__':
    build_visual__database()
