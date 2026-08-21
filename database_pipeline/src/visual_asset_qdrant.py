from pathlib import Path
import pandas as pd
from src.config import PROCESSED_DIR, PROJECT_ROOT
import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client import models

DATABASE_DIR = PROCESSED_DIR / "databases"

HF_REPO_ID = "pranaybannu/COURSEERA_ALMAX_VISUALS"
HF_REPO_TYPE = "dataset"
HF_REVISION = "main"

COLLECTION_NAME = "COURSEERA_ALMAX_MULTIMODAL"
RETRIEVAL_BATCH_SIZE = 100

load_dotenv(PROJECT_ROOT / ".env")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

ASSET_PAYLOAD_FIELDS = {
    "asset_provider",
    "asset_repo_id",
    "asset_repo_type",
    "asset_revision",
    "asset_path",
    "mime_type",
}

UPDATE_BATCH_SIZE = 50


#------------------------------------------------------------------------------
##loading database
#------------------------------------------------------------------------------

def load_database(database_name:str)->pd.DataFrame:

    database_path = DATABASE_DIR / f"{database_name}.csv"

    if not database_path.exists():
        raise FileNotFoundError(f"Database file not found: {database_path}")

    database = pd.read_csv(database_path)

    if database.empty:
        raise ValueError(f"Database is empty: {database_name}")

    if database['record_id'].isna().any():
        raise ValueError(f"Missing record_id in {database_name} database")

    if database['record_id'].duplicated().any():
        raise ValueError(f"Duplicate record_id in {database_name} database")

    return database

#------------------------------------------------------------------------------
## build slide assets
#------------------------------------------------------------------------------

def build_slide_assets(slide_database:pd.DataFrame)->list[dict]:

    assets=[]

    required_columns={
        'record_id',
        'lecture_id',
        'image_file_name',
    }

    missing_columns = required_columns - set(slide_database.columns)

    if missing_columns:
        raise ValueError(f"Missing columns in slide database: {missing_columns}")

    for row in slide_database.to_dict(orient='records'):

        lecture_id = str(row['lecture_id']).strip()
        filename = str(row['image_file_name']).strip()

        if not filename.lower().endswith('.png'):
            raise ValueError(f"Invalid side image file name with extension: {filename}")

        asset_path= (Path("slides")/lecture_id/filename).as_posix()

        assets.append({
            "record_id":str(row['record_id']).strip(),
            'content_type':'slide',
            'asset_provider':'HuggingFace',
            'asset_repo_id':HF_REPO_ID,
            'asset_repo_type':HF_REPO_TYPE,
            'asset_revision':HF_REVISION,
            'asset_path':asset_path,
            'mime_type':'image/png',
        })
    return assets

#------------------------------------------------------------------------------
## build frame assets
#------------------------------------------------------------------------------

def build_frame_assets(frame_database:pd.DataFrame)->list[dict]:

    assets=[]

    required_columns={
        'record_id',
        'lecture_id',
        'frame_filename',
    }

    missing_columns = required_columns - set(frame_database.columns)

    if missing_columns:
        raise ValueError(f"Missing columns in frame database: {missing_columns}")

    for row in frame_database.to_dict(orient='records'):

        lecture_id = str(row['lecture_id']).strip()
        filename = str(row['frame_filename']).strip()

        if not filename.lower().endswith(('.jpg','.jpeg')):
            raise ValueError(f"Invalid frame image file name with extension: {filename}")

        asset_path= (Path("frames")/lecture_id/filename).as_posix()

        assets.append({
            "record_id":str(row['record_id']).strip(),
            'content_type':'frame',
            'asset_provider':'HuggingFace',
            'asset_repo_id':HF_REPO_ID,
            'asset_repo_type':HF_REPO_TYPE,
            'asset_revision':HF_REVISION,
            'asset_path':asset_path,
            'mime_type':'image/jpeg',
        })
    return assets

#------------------------------------------------------------------------------
##validate assets
#------------------------------------------------------------------------------

def validate_assets(assets:list[dict])->None:

    record_ids = [asset['record_id'] for asset in assets]
    asset_paths = [asset['asset_path'] for asset in assets]

    if len(record_ids) != len(set(record_ids)):
        raise ValueError(f"Duplicate record_ids in assets: {record_ids}")

    if len(asset_paths) != len(set(asset_paths)):
        raise ValueError(f"Duplicate asset_paths in assets: {asset_paths}")


#-------------------------------------------------------------------------------
## client for interacting with qdrant
#-------------------------------------------------------------------------------

def create_client()->QdrantClient:
    if not QDRANT_URL:
        raise ValueError("QDRANT_RL IS MISSING FROM ENVIRONMENT (.env)")

    if not QDRANT_API_KEY:
        raise ValueError("QDRANT_API_KEY IS MISSING FROM ENVIRONMENT (.env)")
    
    return QdrantClient(url=QDRANT_URL,
                        api_key=QDRANT_API_KEY,
                        timeout=120)

#-------------------------------------------------------------------------------
# creating a point id
#-------------------------------------------------------------------------------
def create_point_id(record_id:str)->str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, record_id))


#-------------------------------------------------------------------------------
#read only qdrant match validation
#-------------------------------------------------------------------------------

def validate_qdrant_matches(client:QdrantClient,
                            assets:list[dict],)->None:

    missing_records =[]
    mismatched_records =[]
    matched_count = 0

    for start in range(0, len(assets), RETRIEVAL_BATCH_SIZE):
        batch = assets[start:start+RETRIEVAL_BATCH_SIZE]

        expected_by_point_id = {
            create_point_id(asset['record_id']):asset
            for asset in batch
        }

        points = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=list(expected_by_point_id),
            with_payload=['record_id','content_type'],
            with_vectors=False,)

        returned_by_id = {
            str(point.id):point
            for point in points
        }

        for point_id, asset in expected_by_point_id.items():

            point = returned_by_id.get(point_id)

            if point is None:
                missing_records.append(asset['record_id'])
                continue


            payload = point.payload or {}
            if (
                payload.get('record_id') != asset['record_id']
                or payload.get('content_type') != asset['content_type']
            ):
                mismatched_records.append({
                    'expected':asset,
                    "actual":payload,
                })
                continue
            matched_count+=1


    print(f"qdrant visual records matched: {matched_count}")
    print(f"qdrant visual records missing: {len(missing_records)}")
    print(f"qdrant visual records mismatched: {len(mismatched_records)}")

    if missing_records:
        print("missing qdrant records:",missing_records[:3])

    if mismatched_records:
        print("mismatched qdrant records:",mismatched_records[:3])

    if missing_records or mismatched_records:
        raise ValueError("qdrant visual asset mismatch,validation failed, payloads update was not completed")


#-------------------------------------------------------------------------------
# # getting asset payloads
# #------------------------------------------------------------------------------

def get_asset_payload(asset:dict)->dict:

    return {
        key:asset[key]
        for key in ASSET_PAYLOAD_FIELDS
    }

##-----------------------------------------------------------------------------
## update sample assets
##-----------------------------------------------------------------------------

def update_all_visual_assets(client:QdrantClient,
                         assets:list[dict],)->None:


    updated_count = 0

    for start in range(0, len(assets), UPDATE_BATCH_SIZE):

        batch = assets[start:start+UPDATE_BATCH_SIZE]

        operations =[
            models.SetPayloadOperation(
                set_payload=models.SetPayload(
                    payload=get_asset_payload(asset),
                    points=[create_point_id(asset['record_id'])],
                    )
                    )
            
            for asset in batch
        ]

        client.batch_update_points(
            collection_name=COLLECTION_NAME,
            update_operations=operations,
            wait=True,
        )

        updated_count += len(batch)

        print(f"visual payload updated: {updated_count}/{len(assets)}")

##-----------------------------------------------------------------------------#
##validate sample assets
##-----------------------------------------------------------------------------
def validate_all_asset_payloads(client:QdrantClient,
                            assets:list[dict],)->None:


    validated_count =0
    invalid_records=[]

    for start in range(0, len(assets), RETRIEVAL_BATCH_SIZE):
        batch = assets[start:start+RETRIEVAL_BATCH_SIZE]

        expected_by_point_id = {
            create_point_id(asset['record_id']):asset
            for asset in batch
            }

        points = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=list(expected_by_point_id),
            with_payload=list(ASSET_PAYLOAD_FIELDS),
            with_vectors=False,)


        returned_by_id = {
            str(point.id):point
            for point in points
        }

        for point_id, expected_asset in expected_by_point_id.items():

            point = returned_by_id.get(point_id)

            if point is None:
                invalid_records.append({
                    'record_id':expected_asset['record_id'],
                    "reason":"point not found"
                })
                continue


            actual_payload = point.payload or {}

            expected_payload = get_asset_payload(expected_asset)

            incorrect_fields={
                {
                    'expected':expected_value,
                    "actual":actual_payload.get(key),
                }
                for key,expected_value in expected_payload.items()
                if actual_payload.get(key) != expected_value
            }


            if incorrect_fields:
                invalid_records.append({
                    'record_id':expected_asset['record_id'],
                    'incorrect_fields':incorrect_fields,
                })
                continue

            validated_count+=1
            
    print(f"qdrant visual records validated: {validated_count}/{len(assets)}")

    print(f"invalid qdrant visual records: {len(invalid_records)}")

    if invalid_records:
        print("invalid qdrant records:",invalid_records[:3])

        raise ValueError("qdrant visual asset mismatch,validation failed, payloads update was not completed")
        

#------------------------------------------------------------------------------
## main function
#------------------------------------------------------------------------------

def main()->None:

    slide_database = load_database(database_name="slide_database")
    frame_database = load_database(database_name="frame_database")

    slide_assets = build_slide_assets(slide_database)
    frame_assets = build_frame_assets(frame_database)

    all_assets = slide_assets + frame_assets
    validate_assets(all_assets)

    print(f"slide payload preview: {len(slide_assets)}")
    print(f"frame payload preview: {len(frame_assets)}")
    print(f"all payload preview: {len(all_assets)}")

    print("\n slide sample asset:")
    print(slide_assets[0])

    print("\n frame sample asset:")
    print(frame_assets[0])

    print("\n  dry run completed successfully")

    client = create_client()

    point_count = client.count(COLLECTION_NAME,exact=True).count

    print(f"current qdrantp points: {point_count}")

    validate_qdrant_matches(client=client,
                            assets=all_assets)

    print("\n read only qdrant validation completed successfully")
    print("qdrant payloads and vectors were not updated")

    #------------------------------------------------------------------------------

    point_count_before = client.count(COLLECTION_NAME,exact=True).count

    update_all_visual_assets(client=client,
                         assets=all_assets)
                         

    validate_all_asset_payloads(client=client,
                            assets=all_assets)
    
    point_count_after = client.count(COLLECTION_NAME,exact=True).count

    if point_count_before != point_count_after:
        raise ValueError("qdrant point changed from {point_count_before} to {point_count_after}")

    print(f"point count before: {point_count_before}")
    print(f"point count after: {point_count_after}")
    print("allasset payloads updated successfully")

#------------------------------------------------------------------------------
if __name__ == "__main__":
    main()