import os
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from google.genai import types
from pydantic import BaseModel
from google import genai
import time
import re
import json

from src.config import (MAX_API_RETRIES,PROCESSED_DIR, API_RETRY_DELAY, 
                        PROJECT_ROOT, SOURCE_DIR,VISUAL_ANALYSIS_MODEL,
                        generate_lecture_id)

#------------------------------------------------------------------------------
##gemini clientS
#------------------------------------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=gemini_api_key)


#------------------------------------------------------------------------------
##starndard gemini output schema
#------------------------------------------------------------------------------

class VisualAnalysis(BaseModel):
    summary:str                      ##for summary of the slide, string (mostly one liner)
    visual_types:list[str]                 #for indicating the type of visual --> graph, image, flowchart
    visual_text: str                      ##visual descriptor
    diagram_explanation: Optional[str]    ##for detail explanation of diagram , None or text
    graph_explanation:Optional[str]       ##for explaing graph none or text
    equations:list[str]                   ## list containing equations and their meaning
    key_concepts:list[str]                 ## list of key concepts explained in the slide
    visual_text_relation:str              ## explains how visual types support text/written explanation
    content_category:str                  ##for indicating the content category
    needs_human_review: bool             ##True or
    is_instructional_evidence: bool      ##True or

class AllVisualModelsQuotaExhausted(RuntimeError):
    "raised when all models are exhausted"
    pass

#------------------------------------------------------------------------------#
# prompt creation for a slide or frame
# ------------------------------------------------------------------------------#
def create_visual_prompt(
        source_type: str,
        lecture_id: str,
        record_label: str,) ->str:

    if source_type == "slide":
        return f"""
    analyse {record_label} from l{lecture_id} of a university machine-learning and deep learngin course

        Inspect only information visible in the slide:
        1. Written text and headings.
        2. Diagrams, flows and computation graphs.
        3. Graph titles, axes, trends and comparisons.
        4. Tables and their visible information.
        5. Equations, variables and mathematical notation.
        6. Images, labels and annotations.
        7. The relationship between text and visual elements.
        
        INSTRUCTIONS:
        - Summarize the information taught by the slide.
        - List only visual types actually present.
        - Transcribe important readable text.
        - Explain diagrams and graphs factually.
        - show clear mathematical notation./ clear equations, symbols, and variables.
        - Record important visible equations.
        - Do not introduce information absent from the slide.
        - Use one content_category:
          instructional_visual, title_or_section_screen,
          administrative, transition_or_blank, or other.
        - Set is_instructional_evidence to True when the slide
          provides useful course information.
        - Set needs_human_review to True when content is unclear,
          incomplete, unreadable or ambiguous."""

    elif source_type == "frame":
        return f"""
        analyse {record_label} from l{lecture_id} of a university machine-learning and deep learngin course

        Inspect only information visible in the video frame:
        1. Written text and headings.
        2. slides,borads,diragrams, equations flows and computation graphs.
        3. Graph titles, axes, trends and comparisons.
        4. Tables and their visible information.
        5. Equations, variables and mathematical notation.
        6. Images, labels and annotations.
        7. The relationship between text and visual elements.
        8. concepts directly related to the video content
        9. demonstrations, annotations, and explanations.

        INSTRUCTIONS:
        - Do not infer information from the associated caption.
        - Do not introduce information absent from the image.
        - Use one content_category:
        instructional_visual, instructional_visual_with_lecturer,
        lecturer_only, title_or_section_screen, administrative,
        transition_or_blank, or other.
        - Set is_instructional_evidence to True only when the frame
        visibly supports instructional content.
        - Licensing, blank, transition and lecturer-only frames should
        normally be False.
        - Set needs_human_review to True when the frame is unclear
        or its evidence value is uncertain."""

#------------------------------------------------------------------------------##
# analyse one visual record using gemini
#------------------------------------------------------------------------------##

def analyse_image(
        image_path: Path,
        source_type:str,
        lecture_id:str,
        record_label:str,
        unavailable_models:Optional[set[str]]=None) -> dict:

    if unavailable_models is None:
        unavailable_models = set()

    if not image_path.exists():
        raise FileNotFoundError(f"image file not found in: {image_path}")

    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()

    mime_type = ("image/png" if image_path.suffix.lower() == ".png" else "image/jpeg")

    last_quota_error=None

    for model_name in VISUAL_ANALYSIS_MODEL:

        ##skipping models that are unavailable
        if model_name in unavailable_models:
            continue

        switch_without_disabling = False ##for other errors

        for retry_number in range(1,MAX_API_RETRIES+1):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        create_visual_prompt(
                            source_type,
                            lecture_id,
                            record_label,
                        ),
                        types.Part.from_bytes(
                        data=img_bytes,
                        mime_type=mime_type,),
                    ],
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=VisualAnalysis,),
                )

                # Gemini normally returns structured JSON as text.
                if response.text:
                    analysis = VisualAnalysis.model_validate_json(
                        response.text
                    )

                # Some SDK/model combinations return an already parsed result.
                ## this is for gemma model
                elif getattr(response, "parsed", None) is not None:
                    parsed_response = response.parsed

                    if isinstance(parsed_response, VisualAnalysis):
                        analysis = parsed_response
                    else:
                        analysis = VisualAnalysis.model_validate(
                            parsed_response
                        )

                # Gemma may/might return the schema through automatic function calling.
                elif getattr(response, "function_calls", None):
                    analysis = VisualAnalysis.model_validate(
                        response.function_calls[0].args
                        )

                else:
                    raise ValueError(
                        f"{model_name} returned no text or structured result"
                    )

                result = analysis.model_dump()

                result['model_used']=model_name

                return result

            except Exception as e:

                error_text=str(e).lower()

                empty_response_error = ("returned no text or structured result"in error_text)

                if empty_response_error:
                    print(f"{model_name} returned an empty response; switching to the next model")

                    switch_without_disabling = True
                    break

                quota_error = ("429" in error_text or "quota exceeded" in error_text or 'resource_exhausted' in error_text)
        
                if not quota_error:
                    raise 

                last_quota_error=e

                if retry_number< MAX_API_RETRIES:

                    wait_seconds = (2**retry_number)

                    print(f"{model_name} quota error, retrying in {wait_seconds} seconds")
                    time.sleep(wait_seconds)


        if switch_without_disabling:
            continue

        unavailable_models.add(model_name)
        print(f"{model_name} quota unavailable, switching to next model")

    # All available models responded, but none produced usable
    # structured content for this specific image.
    if last_quota_error is None:
        return {
            "summary": (
                "Visual analysis was unavailable because all "
                "configured models returned an empty response."
            ),
            "visual_types": [],
            "visual_text": "",
            "diagram_explanation": None,
            "graph_explanation": None,
            "equations": [],
            "key_concepts": [],
            "visual_text_relation": "",
            "content_category": "other",
            "needs_human_review": True,
            "is_instructional_evidence": False,
            "model_used": None,
        }

    # At least one model was unavailable because of quota.
    raise AllVisualModelsQuotaExhausted("All configured visual models exhausted their quotas.") from last_quota_error
    
    

#------------------------------------------------------------------------------
## testin gemini api on  one frame and slide
#------------------------------------------------------------------------------
def test_gemini_visual_analysis() -> None:
    master_dir = PROCESSED_DIR / "master"

    slide_manifest_df = pd.read_csv(master_dir/'slide_manifest.csv')

    frame_manifest_df = pd.read_csv(master_dir/'caption_linked_lecture_frames_manifest.csv')

    test_slide = slide_manifest_df.iloc[0]

    slide__result = analyse_image(
        image_path=Path(test_slide['image_file_path']),
        source_type="slide",
        lecture_id=test_slide['lecture_id'],
        record_label= (f"slide {int(test_slide['slide_no'])}"),
    )

    test_frame = frame_manifest_df.iloc[0]
    frame_result = analyse_image(
        image_path = Path(test_frame['frame_file_path']),
        source_type="frame",
        lecture_id=test_frame['lecture_id'],
        record_label= test_frame['frame_id'],
    )

    print("slide test completed")

    print("slide_category:", slide__result['content_category'])

    print("slide instructional_evidence:", slide__result['is_instructional_evidence'])

    print("\nframe test completed")

    print("frame_category:", frame_result['content_category'])

    print("frame instructional_evidence:", frame_result['is_instructional_evidence'])


#------------------------------------------------------------------------------
## create visual processing queue
#------------------------------------------------------------------------------

def create_visual_processing_queue()->list[dict]:
    """combine all slide and caption linked frame records"""
    master_dir = PROCESSED_DIR / "master"

    slide_manifest_df = pd.read_csv(master_dir/'slide_manifest.csv')

    frame_manifest_df = pd.read_csv(master_dir/'caption_linked_lecture_frames_manifest.csv')

    # Support manifests created before the spelling correction.
    if ("extarction_status" in frame_manifest_df.columns
        and "extraction_status"
        not in frame_manifest_df.columns):

        frame_manifest_df = frame_manifest_df.rename(
            columns={"extarction_status": "extraction_status"})

    processing_queue=[]

    for _,slide in slide_manifest_df.iterrows():

        lecture_id = slide['lecture_id']
        lecture_number = int(re.search(r"\d+", lecture_id).group())
        slide_number = int(slide['slide_no'])

        lecture_ids = generate_lecture_id(lecture_id)

        processing_queue.append({
            'visual_record_id':f"SLIDE_LEC{lecture_number:02d}_{slide_number:03d}",
            'source_type':'slide',
            'source_asset_id':lecture_ids['slide_asset_id'],
            'lecture_id':lecture_id,
            'slide_no':slide_number,
            'frame_id':None,
            'primary_chunk_id':None,
            'timestamp_seconds':None,
            'image_file_path':slide['image_file_path'],
            'record_label':f"slide {slide_number}",
        })

    ##adding all sucessfully extracted caption_linked_frames
    completed_frames = frame_manifest_df[frame_manifest_df['extraction_status']=='complete']

    for _,frame in completed_frames.iterrows():
        processing_queue.append({
            'visual_record_id':frame['frame_id'],
            'source_type':'frame',
            'source_asset_id':frame['asset_id'],
            'lecture_id':frame['lecture_id'],
            'slide_no':None,
            'frame_id':frame['frame_id'],
            'primary_chunk_id':frame['primary_chunk_id'],
            'timestamp_seconds':frame['timestamp_seconds'],
            'image_file_path':frame['frame_file_path'],
            'record_label':frame['frame_id'],
        })

    return processing_queue

#------------------------------------------------------------------------------
##checkpoints json
#------------------------------------------------------------------------------

def load_visual_checkpoints(checkpoint_path:Path)->list[dict]:
    """load checkpoints from json file"""
    if not checkpoint_path.exists():
        return []

    records=[]

    with open(checkpoint_path, "r", encoding='utf-8') as checkpoint_file:

        for line_number,line in enumerate(checkpoint_file,start=1):

            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"skipping invalid checkpoint line {line_number}: {line}")

    return records

#------------------------------------------------------------------------------
##appendding one successfull gemini result
#------------------------------------------------------------------------------

def append_visual_checkpoints(checkpoint_path:Path,records:dict)->None:

    with open(checkpoint_path, "a", encoding='utf-8') as file:

        file.write(json.dumps(records,ensure_ascii=False)+'\n')


#------------------------------------------------------------------------------
## analyse all slides and caption linked frames
#------------------------------------------------------------------------------

def run_complete_visual_analysis()->pd.DataFrame:
    """run visual analysis on all slides and caption linked frames"""

    master_dir = PROCESSED_DIR / "master"

    checkpoint_path = master_dir / "geminivisual_analysis_checkpoints.json"

    output_csv_path = master_dir / "gemini_visual_analysis.csv"

    output_json_path = master_dir / "gemini_visual_analysis.json"

    processing_queue = create_visual_processing_queue()

    results = load_visual_checkpoints(checkpoint_path)

    completed_ids ={record['visual_record_id'] for record in results}


    ##models added here are skipped if they are unavailable

    unavailable_models: set[str] = set()

    quota_exhausted = False

    print('visual records expected:',len(processing_queue))

    print('previously completed:',len(completed_ids))


    for index,record in enumerate(processing_queue,start=1):

        visual_record_id = record['visual_record_id']

        if visual_record_id in completed_ids:
            continue

        try:
            print(f"[{index}/{len(processing_queue)}] analyzing {visual_record_id}")

            analysis = analyse_image(
                image_path=Path(record['image_file_path']),
                source_type=record['source_type'],
                lecture_id=record['lecture_id'],
                record_label=record['record_label'],
                unavailable_models=unavailable_models,
            )

            ##adding database linking metadata

            analysis.update({
                "visual_record_id":visual_record_id,
                'source_type':record['source_type'],
                'source_asset_id':record['source_asset_id'],
                'lecture_id':record['lecture_id'],
                'slide_no':record['slide_no'],
                'frame_id':record['frame_id'],
                'primary_chunk_id':record['primary_chunk_id'],
                'timestamp_seconds':record['timestamp_seconds'],
                'image_file_path':record['image_file_path'],
            })

            ##save immdediately to avoid quota errors

            append_visual_checkpoints(checkpoint_path,analysis)

            results.append(analysis)

            completed_ids.add(visual_record_id)

            ##sleep to avoid quota errors
            time.sleep(API_RETRY_DELAY)

        except AllVisualModelsQuotaExhausted:

            print(f"All models exhausted their quotas, skipping {visual_record_id}")

            print('stopping save to avoid quota errors')

            quota_exhausted=True
            break

        except Exception as e:

            ##a bad record remains absent from the checkpoints
            ##will be retried on next run

            print(f"{visual_record_id} failed with error: {type(e).__name__}: {e}")

    visual_analysis_df = pd.DataFrame(results)

    if not visual_analysis_df.empty:

        visual_analysis_df = (
            visual_analysis_df.drop_duplicates(subset=['visual_record_id'],
                                               keep='last').sort_values(by=
                                                                        ['lecture_id','source_type','visual_record_id']).reset_index(drop=True))


        visual_analysis_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

        with open(output_json_path, "w", encoding='utf-8') as file:
            json.dump(visual_analysis_df.to_dict(orient='records'),file,ensure_ascii=False,indent=2)

        print('\n visual analysis completed')

        print('expected records:',len(processing_queue))

        print('completed records:',len(visual_analysis_df))

        print("remaining records:",len(processing_queue)-len(visual_analysis_df))

        print('stoped due to quota exhaustion:',quota_exhausted)

        return visual_analysis_df
    
if __name__ == "__main__":
    run_complete_visual_analysis()

