##GENERATING EMBEDDINGS FOR QUIZ AND DISCUSSION DATABASES
import ast
from pathlib import Path
import json
import pandas as pd
from typing import Any, Optional
from sentence_transformers import SentenceTransformer
from src.config import PROCESSED_DIR

DATABASE_DIR = PROCESSED_DIR / "databases"
EMBEDDING_DIR = PROCESSED_DIR / "embeddings"

MODEL_NAME ="BAAI/bge-base-en-v1.5"
EMBEDDING_DIMENSIONS = 768
BATCH_SIZE = 35

EXPECTED_COUNT = {
    "quiz_database":456,
    "discussion_database":570,   
}

#------------------------------------------------------------------------------
## parsing serialzed lists and dicts into python objects
#------------------------------------------------------------------------------

def parse_serialized_value(value: Any) -> Any:

    if value is None:
        return None

    if isinstance(value, (list, dict)):
        return value

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if not isinstance(value, str):
        return value

    value = value.strip()

    if not value:
        return None

    if value.startswith(('[', '{')):

        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value
    
    return value

3#------------------------------------------------------------------------------
## converting database values into readable embedding text
#------------------------------------------------------------------------------

def format_for_embedding(value: Any) -> str:

    value = parse_serialized_value(value)

    if value is None:
        return ""

    if isinstance(value, dict):
        return "; ".join(
            f"{key}:{format_for_embedding(item)}"
            for key, item in value.items())

    if isinstance(value, list):
        return ", ".join(format_for_embedding(item) for item in value)

    return str(value).strip()

#------------------------------------------------------------------------------
# constructing one searchable text for one quizz record
#------------------------------------------------------------------------------
def build_quiz_text(row:pd.Series)->str:

    feilds=[
        ("Question", row.get("question")),
        ("Options", row.get("options")),
        ("Correct answer", row.get("correct_answer")),
        ("Explanation", row.get("explanation")),
        ("Topic", row.get("topic")),
        ("Difficulty", row.get("difficulty_signals")),
        ("Concept tags", row.get("concept_tags")),
        ("Question type", row.get("question_type")),
    ]

    return "\n".join(f"{label}:{formatted}"
                     for label,value in feilds
                     if (formatted:= format_for_embedding(value)))
    
#------------------------------------------------------------------------------
# constructing one searchable text for one discussion record
#------------------------------------------------------------------------------

def build_discussion_text(row:pd.Series)->str:

    feilds=[
        ("Thread title", row.get("thread_title")),
        ("Post", row.get("post_text")),
        ("Topic", row.get("topic")),
        ("Recurring theme", row.get("recurring_theme")),
        ("Concept tags", row.get("concept_tags")),
        ("Sentiment", row.get("sentiment")),
        ("Friction type", row.get("friction_type")),
        ("Severity", row.get("severity")),
    ]

    return "\n".join(f"{label}:{formatted}"
                     for label,value in feilds
                     if (formatted:= format_for_embedding(value)))

#------------------------------------------------------------------------------
##loading database and validate its required identifiers
#------------------------------------------------------------------------------

def load_and_validate_database(database_name:str)->pd.DataFrame:

    database_path = DATABASE_DIR / f"{database_name}.csv"

    if not database_path.exists():
        raise FileNotFoundError(f"Database file not found: {database_path}")

    database_df = pd.read_csv(database_path)

    expected_count = EXPECTED_COUNT[database_name]

    if len(database_df) != expected_count:
        raise ValueError(f"Expected {expected_count} records in {database_name} database, found {len(database_df)}")

    required_columns = {
        "record_id",
        "lecture_id",
    }

    missing_columns = required_columns - set(database_df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns in {database_name} database: {missing_columns}")

    if database_df['record_id'].isna().any():
        raise ValueError(f"Missing record_id in {database_name} database")

    if database_df['record_id'].duplicated().any():
        raise ValueError(f"Duplicate record_id in {database_name} database")

    if database_df['lecture_id'].isna().any():
        raise ValueError(f"Missing lecture_id in {database_name} database")

    return database_df

#------------------------------------------------------------------------------
##generating embedding and saving embeddings for one database
#------------------------------------------------------------------------------

def generate_embeddings(model:SentenceTransformer,
                        database_name:str,
                        content_type:str)->None:

    database_df = load_and_validate_database(database_name)

    if content_type=="quiz":

        searchable_texts = [
            build_quiz_text(row)
            for _, row in database_df.iterrows()
        ]
    elif content_type=="discussion":

        searchable_texts = [
            build_discussion_text(row)
            for _, row in database_df.iterrows()
        ]
    else:
        raise ValueError(f"Invalid content type: {content_type}")


    empty_text_ids =[
        database_df.iloc[index]["record_id"]
        for index,text in enumerate(searchable_texts)
        if not text.strip()
    ]

    if empty_text_ids:
        raise ValueError(f"{database_name} database has empty text ids: {empty_text_ids[:10]}")

    print(f"\n Generating {len(searchable_texts)} embeddings for {content_type}")

    vectors= model.encode(searchable_texts,
                          batch_size=BATCH_SIZE,
                          show_progress_bar=True,
                          convert_to_numpy=True,
                          normalize_embeddings=True,)

    if vectors.shape != (len(database_df),EMBEDDING_DIMENSIONS):
        raise ValueError(f"uneexpected embedding shape for {database_name} database: {vectors.shape}")

    embedding_records=[]

    for row_index,row in database_df.iterrows():
        embedding_records.append({
            'record_id':str(row['record_id']),
            'lecture_id':str(row['lecture_id']),
            'content_type':content_type,
            'embedding_model':MODEL_NAME,
            'embedding_dimensions':EMBEDDING_DIMENSIONS,
            'embedding':vectors[row_index].astype(float).tolist(),
        })

    output_path = (EMBEDDING_DIR / f"{database_name}_embeddings.json")

    temporary_path = output_path.with_suffix(".json.tmp")

    if output_path.exists():
        raise FileExistsError(f"Output file already exists: {output_path}")

    EMBEDDING_DIR.mkdir(parents=True, exist_ok=True)

    with open(temporary_path,'w',encoding='utf-8') as file:
        json.dump(embedding_records,file,ensure_ascii=False)

    temporary_path.replace(output_path)
    print(f"Saved {len(embedding_records)} embeddings to {output_path}")

#------------------------------------------------------------------------------
#genarating quizz and discussion database
#--------------------------------------------------------------------------------
def main()->None:
    print('loading embedding model: ', MODEL_NAME)

    model= SentenceTransformer(MODEL_NAME)

    ## generating embeddings for quiz database
    generate_embeddings(model=model,
                        database_name="quiz_database",
                        content_type="quiz")

    ## generating embeddings for discussion database
    generate_embeddings(model=model,
                        database_name="discussion_database",
                        content_type="discussion")

    print("\n quiz and discussion embeddings generated")


if __name__ == "__main__":
    main()
    
    