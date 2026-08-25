##GENERATING EMBEDDINGS FOR CAPTION, SLIDE AND FRAME DATABSES

import json
import time
from pathlib import Path
import pandas as pd
from sentence_transformers import SentenceTransformer


from src.config import PROCESSED_DIR, PROJECT_ROOT,EMBEDDING_MODEL,EMBEDDING_DIMENSIONS


DATABASE_DIR = PROCESSED_DIR / "databases"
EMBEDDING_DIR = PROCESSED_DIR / "embeddings"
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

##EMBEDDING BATCH SIZE
EMBEDDING_BATCH_SIZE = 32



#------------------------------------------------------------------------------\
## loaading the database
#------------------------------------------------------------------------------

def load_database(database_name:str,) -> pd.DataFrame:

    database_path = DATABASE_DIR / f"{database_name}.csv"

    if not database_path.exists():
        raise FileNotFoundError(f"Database file {database_path} not found")

    database_df = pd.read_csv(database_path)


    if database_df['record_id'].duplicated().any():
        raise ValueError(f"Duplicate records found in {database_name} database")

    return database_df


#------------------------------------------------------------------------------
## embeddig on textdata
#------------------------------------------------------------------------------

def embedding_text(database_df:pd.DataFrame,
                   database_name:str,) -> pd.DataFrame:


    database_df = database_df.copy()


    if database_name == 'caption_database':

        database_df['embedding_text'] =(
            database_df['text'].fillna("").astype(str)  
        )

    else:
        database_df['embedding_text'] = (
            database_df['searchable_text'].fillna("").astype(str))

    ##removing empty strings
    database_df = database_df[database_df['embedding_text'].str.strip() !=""].copy()


    return database_df.reset_index(drop=True)

#------------------------------------------------------------------------------
## embedding checkpoints
#------------------------------------------------------------------------------

def load_embedding_checkpoint(checkpoint_path:Path)->list[dict]:

    ## loading successfullt generated embeddings

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
            except json.JSONDecodeError as e:
                print(f"skipping invalid checkpoint line {line_number}: {line}")
                continue
    return records

#------------------------------------------------------------------------------
## appending successful embeddings
#------------------------------------------------------------------------------

def append_embedding_checkpoint(checkpoint_path:Path,records:dict)->None:

    ##immediately saving the sucessfull embeddings to checkpoints
    with open(checkpoint_path, "a", encoding='utf-8') as file:
        file.write(json.dumps(records,ensure_ascii=False)+'\n')


#------------------------------------------------------------------------------
## GENERATE EMBEDDINGS PER BATCH
#------------------------------------------------------------------------------

def generate_embeddings(texts:list[str],) ->list[list[float]]:

    embeddings = embedding_model.encode(texts,
                                        batch_size=EMBEDDING_BATCH_SIZE,
                                        show_progress_bar=False,
                                        normalize_embeddings=True,
                                        convert_to_numpy=True,)

    return embeddings.tolist()

#------------------------------------------------------------------------------
## GENERATE EMBEDDINGS FOR DATABASE
#------------------------------------------------------------------------------

def generate_database_embeddings(database_name:str,)->Path:

    EMBEDDING_DIR.mkdir(parents=True,exist_ok=True)

    database_df = load_database(database_name)

    database_df = embedding_text(database_df,database_name)

    checkpoint_path = EMBEDDING_DIR / f"{database_name}_embedding_checkpoints.jsonl"

    output_path = EMBEDDING_DIR / f"{database_name}_embeddings.json"

    embedding_records = load_embedding_checkpoint(checkpoint_path)

    completed_ids ={record['record_id'] for record in embedding_records}


    pending_df = database_df[~ database_df['record_id'].isin(completed_ids)].copy()


    print('\n',database_name,'database:')
    print('records expected:',len(database_df))
    print('previously completed:',len(completed_ids))
    print('pending records:',len(pending_df))


    for batch_start in range(0,len(pending_df),EMBEDDING_BATCH_SIZE):

        batch_df= pending_df.iloc[batch_start:batch_start+EMBEDDING_BATCH_SIZE]

        texts = batch_df['embedding_text'].tolist()

        embeddings = generate_embeddings(texts)

        if len(embeddings)!=len(batch_df):
            raise ValueError(f"embeddings batch size mismatch: {len(embeddings)} != {len(batch_df)}")

        for (_,row), embedding in zip(batch_df.iterrows(),embeddings):

            embedding_record = {
                'record_id':row['record_id'],
                'lecture_id':row['lecture_id'],
                'content_type':row['content_type'],
                'embedding_model':EMBEDDING_MODEL,
                'embedding_dimensions':EMBEDDING_DIMENSIONS,
                'embedding':embedding,}

            append_embedding_checkpoint(checkpoint_path,embedding_record)

            embedding_records.append(embedding_record)

            print(f"embedded: {len(embedding_records)}/{len(database_df)}")


    with open(output_path, "w", encoding='utf-8') as file:

        json.dump(embedding_records,file,ensure_ascii=False)

    print('saved embedding checkpoints to',output_path)
    return output_path

#------------------------------------------------------------------------------
## generate all database embeddings
#------------------------------------------------------------------------------
def generate_all_database_embeddings()->None:
    database_names = [
        'caption_database',
        'slide_database',
        'frame_database',
    ]

    for database_name in database_names:
        generate_database_embeddings(database_name)

    print('all database embeddings completed')


if __name__ == "__main__":
    generate_all_database_embeddings()




