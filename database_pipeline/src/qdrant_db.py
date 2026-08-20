"""Qdrant is a vector database. Instead of searching only for matching words, 
it stores embeddings and searches for records with similar meanings."""


import json
import os
import uuid
from pathlib import Path
from typing import Any, Optional
import pandas as pd
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import ( Distance,PointStruct,VectorParams)

from src.config import (PROCESSED_DIR,PROJECT_ROOT)

DATABASE_DIR = PROCESSED_DIR / "databases"
EMBEDDING_DIR = PROCESSED_DIR / "embeddings"
COLLECTION_NAME = "COURSEERA_ALMAX_MULTIMODAL"
VECTOR_DIMENSIONS = 768
UPLOAD_BATCH_SIZE = 100

load_dotenv(PROJECT_ROOT / ".env")

QDRANT_URL = os.getenv("QDRANT_URL","http://localhost:6333")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

#------------------------------------------------------------------------------
## connecting to qdrant (local or cloud)
#------------------------------------------------------------------------------

def create_qdrant_client()->QdrantClient:

    return QdrantClient(url=QDRANT_URL,api_key=QDRANT_API_KEY,timeout=120,)


#------------------------------------------------------------------------------
##Creating a collection
#------------------------------------------------------------------------------

def create_qdrant_collection(client:QdrantClient)->None:

    existing_collections = {
        collection.name
        for collection in client.get_collections().collections
    }

    if COLLECTION_NAME in existing_collections:
        print("using existing collection",COLLECTION_NAME)
        return
    

    ##creating a new collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_DIMENSIONS,
            distance=Distance.COSINE,
        ),)

    print("created collection",COLLECTION_NAME)


#------------------------------------------------------------------------------
## creating a stable UUid from database record id
#------------------------------------------------------------------------------

def create_point_id(record_id:str)->str:
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            record_id,
        )
    )

# ------------------------------------------------------------------------------
##converting pandas and missing values to qdrant compatible types
# ------------------------------------------------------------------------------

def clean_payload_value(value: Any) -> Any:
    """Convert pandas/NumPy values into Qdrant-compatible values."""

    if value is None:
        return None

    if isinstance(value, (list, dict)):
        return value

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, (bool, int, float, str)):
        return value

    if hasattr(value, "item"):
        return value.item()
    
    return str(value).strip() 

# ------------------------------------------------------------------------------
## loading database records indexed by record_id
# ------------------------------------------------------------------------------

def load_database_records(database_name:str) -> dict[str,dict]:

    database_path = DATABASE_DIR / f"{database_name}.csv"

    database_df = pd.read_csv(database_path)
    
    records = {}

    for record in database_df.to_dict(orient='records'):

        record_id = str(record['record_id'])

        records[record_id] = {
            key:clean_payload_value(value)
            for key,value in record.items()
        }

    return records

#------------------------------------------------------------------------------
# laoding embeddings
#------------------------------------------------------------------------------

def load_embedding_records(database_name:str) -> list[dict]:

    embedding_path = EMBEDDING_DIR / f"{database_name}_embeddings.json"

    if not embedding_path.exists():
        raise FileNotFoundError(f"Embedding file not found: {embedding_path}")

    with open(embedding_path,"r",encoding="utf-8") as file:
        records = json.load(file)

        return records

#------------------------------------------------------------------------------
# building qdrant points, combining vectors with their database metadata
#------------------------------------------------------------------------------

def build_qdrant_points(database_name:str) -> list[PointStruct]:

    database_records = load_database_records(database_name)

    embedding_records = load_embedding_records(database_name)

    qdrant_points=[]

    for embedding_record in embedding_records:
        record_id = str(embedding_record['record_id'])

        if record_id not in database_records:
            raise ValueError(f"{record_id} not found in {database_name} database")


        vector = embedding_record['embedding']

        if len(vector)!=VECTOR_DIMENSIONS:
            raise ValueError(f"{record_id} has invalid embedding dimension: {len(vector)}, expected {VECTOR_DIMENSIONS}")

        payload = database_records[record_id]

        payload['embedding_model'] = embedding_record['embedding_model']

        qdrant_points.append(PointStruct(
            id=create_point_id(record_id),
            vector=vector,
            payload=payload,
        ))

    return qdrant_points

#------------------------------------------------------------------------------
# uploading point in batches
#------------------------------------------------------------------------------

def upload_points(client:QdrantClient,points:list[PointStruct]) -> None:

    for batch_start in range(0,len(points),UPLOAD_BATCH_SIZE):

        batch = points[batch_start:batch_start+UPLOAD_BATCH_SIZE]

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
            wait=True,
        )
        upload_count = min(batch_start+len(batch),len(points))
        print(f"uploaded {upload_count}/{len(points)} points")


#------------------------------------------------------------------------------
## uploading all embeddings to qdrant collection
#------------------------------------------------------------------------------
def upload_all_embeddings()->None:
    client = create_qdrant_client()

    create_qdrant_collection(client)

    database_names = [
        'caption_database',
        'slide_database',
        'frame_database',
    ]

    total_uploaded_=0

    for database_name in database_names:

        print("\n uploading:",database_name)

        points = build_qdrant_points(database_name)

        upload_points(client,points)
        total_uploaded_ += len(points)


    print('\n qdrant upload completed')
    print('collction:',COLLECTION_NAME)
    print('total records uploaded:',total_uploaded_)


if __name__ == "__main__":
    upload_all_embeddings()

    
