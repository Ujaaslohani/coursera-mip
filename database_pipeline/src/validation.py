""" This performs one final check across:
Source databases
Embedding files
Qdrant collection
It confirms record counts, IDs, vector dimensions and Qdrant upload totals. """

import json
from pathlib import Path
import pandas as pd
from src.config import PROCESSED_DIR
from src.qdrant_db import COLLECTION_NAME,VECTOR_DIMENSIONS,create_qdrant_client

DATABASE_DIR = PROCESSED_DIR / "databases"
EMBEDDING_DIR = PROCESSED_DIR / "embeddings"

DATABASE_NAMES = [
    'caption_database',
    'slide_database',
    'frame_database',
]

#------------------------------------------------------------------------------
# LOADING DATABASES
#------------------------------------------------------------------------------

def load_database_records(database_name:str) -> pd.DataFrame:

    database_path = DATABASE_DIR / f"{database_name}.csv"

    if not database_path.exists():
        raise FileNotFoundError(f"Database file not found: {database_path}")

    return pd.read_csv(database_path)

#------------------------------------------------------------------------------
# LOADING EMBEDDINGS
#------------------------------------------------------------------------------
def load_embedding_records(database_name:str) -> list[dict]:

    embedding_path = EMBEDDING_DIR / f"{database_name}_embeddings.json"

    if not embedding_path.exists():
        raise FileNotFoundError(f"Embedding file not found: {embedding_path}")

    with open(embedding_path,"r",encoding="utf-8") as file:
        records = json.load(file)

        return records

#------------------------------------------------------------------------------
# validate ids, counts, and vector dimensions
#------------------------------------------------------------------------------

def validate_one_database(database_name:str) -> dict:

    database_df = load_database_records(database_name)
    embedding_records = load_embedding_records(database_name)


    database_ids = database_df['record_id'].astype(str).tolist()

    embedding_ids = [str(record['record_id']) for record in embedding_records]

    duplicate_database_ids = (len(database_ids) - len(set(database_ids)))
    duplicate_embedding_ids = (len(embedding_ids) - len(set(embedding_ids)))

    missing_embedding_ids = sorted(set(database_ids) - set(embedding_ids))

    unexepected_embedding_ids = sorted(set(embedding_ids) - set(database_ids))

    incorrect_dimensions = [
        record['record_id']
        for record in embedding_records
        if len(record['embedding'])!=VECTOR_DIMENSIONS
    ]

    valid = all([
        duplicate_database_ids==0,
        duplicate_embedding_ids==0,
        not missing_embedding_ids,
        not unexepected_embedding_ids,
        not incorrect_dimensions,
        len(database_ids)==len(embedding_ids),
    ])

    return {
        'database_name':database_name,
        'database_records':len(database_df),
        'embedding_records':len(embedding_records),
        'duplicate_database_ids':duplicate_database_ids,
        'duplicate_embedding_ids':duplicate_embedding_ids,
        'missing_embedding_ids':missing_embedding_ids,
        'unexepected_embedding_ids':unexepected_embedding_ids,
        'incorrect_dimensions':incorrect_dimensions,
        'valid':valid,
    }



#------------------------------------------------------------------------------
# validate qdrant collection
# confirming the final number of qdrant records
#------------------------------------------------------------------------------

def validate_qdrant(expected_total:int) -> dict:

    client = create_qdrant_client()

    count_result = client.count(collection_name=COLLECTION_NAME, exact=True)

    qdrant_points = count_result.count

    return {
        'collection_name':COLLECTION_NAME,
        'expected_points':expected_total,
        'qdrant_points':qdrant_points,
        'valid':qdrant_points==expected_total,
    }

#------------------------------------------------------------------------------
# final project validate
#------------------------------------------------------------------------------

def run_final_validation()->None:

    validation_results=[]

    for  database_name in DATABASE_NAMES:
        result = validate_one_database(database_name)

        validation_results.append(result)

    expected_qdrant_total = sum(result['database_records'] for result in validation_results)

    qdrant_result = validate_qdrant(expected_qdrant_total)

    print("final databse validation")
    print("--"*60)

    for result in validation_results:
        print(f"{result['database_name']}:"
              f"\n\tdatabase records: {result['database_records']}"
              f"\n\tembedding records: {result['embedding_records']}"
              f"\n\tvalidation: {result['valid']}")

        if not result['valid']:
            print("duplicate database ids:",result['duplicate_database_ids'])

            print("duplicate embedding ids:",result['duplicate_embedding_ids'])
            print("missing embedding ids:",result['missing_embedding_ids'])
            print("unexepected embedding ids:",result['unexepected_embedding_ids'])
            print("incorrect embedding dimensions:",result['incorrect_dimensions'])

    print(
        f"{qdrant_result['collection_name']}:"
        f"{qdrant_result['qdrant_points']} points,"
        f"expected {qdrant_result['expected_points']} points,"
        f"validation: {qdrant_result['valid']}"

    )

    completed_database_validation = all(result['valid'] for result in validation_results)

    final_valid = completed_database_validation and qdrant_result['valid']

    print("--"*60)

    if not final_valid:
        raise ValueError("final validation failed")

    print("final validation completed")

if __name__ == "__main__":
    run_final_validation()
