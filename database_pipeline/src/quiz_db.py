# Import required libraries
import os
import json
import time
from pathlib import Path
import pandas as pd

from dotenv import load_dotenv
from google import genai

# STEP 1 — GENERATION PIPELINE PATh

PROJECT_DIR = Path("..")

# Input
PREPROCESSED_DIR = PROJECT_DIR / "03_PREPROCESSED_DATA"

CHUNK_DIR = PREPROCESSED_DIR / "chunks"
TRANSCRIPT_DIR = PREPROCESSED_DIR / "transcript"

# Output
SYNTHETIC_DIR = PROJECT_DIR / "04_SYNTHETIC_DATA"

QUIZ_DIR = SYNTHETIC_DIR / "quiz"
DISCUSSION_DIR = SYNTHETIC_DIR / "discussion"

# Create output folders
QUIZ_DIR.mkdir(parents=True, exist_ok=True)
DISCUSSION_DIR.mkdir(parents=True, exist_ok=True)

print("Project:", PROJECT_DIR.resolve())
print("Chunks:", CHUNK_DIR)
print("Transcripts:", TRANSCRIPT_DIR)
print("Quiz output:", QUIZ_DIR)
print("Discussion output:", DISCUSSION_DIR)


# STEP 2 — LOAD LECTURE 1 CHUNKS


lecture_id = "lec01"

chunk_file = CHUNK_DIR / f"{lecture_id}_caption_chunks.csv"

chunks_df = pd.read_csv(chunk_file)

print("Lecture:", lecture_id)
print("File:", chunk_file)
print("Total chunks:", len(chunks_df))
print("Columns:", list(chunks_df.columns))

display(chunks_df.head(3))

# STEP 3 — VALIDATE CHUNKS

print("Total chunks:", len(chunks_df))

print(
    "Duplicate chunk IDs:",
    chunks_df["chunk_id"].duplicated().sum()
)

print(
    "Missing text:",
    chunks_df["text"].isna().sum()
)

print(
    "Missing timestamps:",
    chunks_df[["start_time", "end_time"]].isna().any(axis=1).sum()
)

print(
    "Missing chunk IDs:",
    chunks_df["chunk_id"].isna().sum()
)

print(
    "Word count range:",
    chunks_df["word_count"].min(),
    "to",
    chunks_df["word_count"].max()
)


# STEP 4 — GEMINI SETUP 

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

print("Gemini client initialized successfully")

# STEP 5 — QUIZ OUTPUT SCHEMA

QUIZ_SCHEMA = {
    "type": "object",
    "properties": {
        "lecture_id": {
            "type": "string"
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string"
                    },
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "correct_answer": {
                        "type": "string"
                    },
                    "explanation": {
                        "type": "string"
                    },
                    "concept_tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "chunk_ids": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "question",
                    "options",
                    "correct_answer",
                    "explanation",
                    "concept_tags",
                    "chunk_ids"
                ]
            }
        }
    },
    "required": [
        "lecture_id",
        "questions"
    ]
}

print("Quiz schema ready")


# STEP 6 — PREPARE BATCHES FOR TOPIC EXTRACTION

BATCH_SIZE = 10

batches = [
    chunks_df.iloc[i:i + BATCH_SIZE]
    for i in range(0, len(chunks_df), BATCH_SIZE)
]

print("Total batches:", len(batches))

for i, batch in enumerate(batches, start=1):
    print(f"Batch {i}: {len(batch)} chunks")


# STEP 7 — GENERATE WITH RETRY

import time


def generate_with_retry(
    model,
    contents,
    config,
    max_retries=5
):
    """
    Call Gemini with automatic retry handling
    for temporary 429 / RESOURCE_EXHAUSTED errors.
    """

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )

            return response

        except Exception as e:

            error_text = str(e)

            # Retry only for quota / rate-limit errors
            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                if attempt == max_retries - 1:
                    raise

                wait_seconds = 10 * (attempt + 1)

                print(
                    f"429 quota/rate limit. "
                    f"Retrying in {wait_seconds}s..."
                )

                time.sleep(wait_seconds)

            else:
                # Do not hide other errors
                raise


print("Gemini retry handler ready")


# STEP 8 — SAFE JSON GEMINI RESPONSE

def generate_json_with_retry(
    model,
    contents,
    config,
    max_retries=5
):

    for attempt in range(max_retries):

        try:

            response = generate_with_retry(
                model=model,
                contents=contents,
                config=config
            )

            text = response.text.strip()

            # Remove markdown code fences if present
            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            return json.loads(text)

        except json.JSONDecodeError as e:

            if attempt == max_retries - 1:
                raise

            wait_seconds = 5 * (attempt + 1)

            print(
                f"Invalid JSON response. "
                f"Retrying in {wait_seconds}s..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError("Failed to obtain valid JSON")


# STEP 9 — TOPIC EXTRACTION FUNCTION

def extract_topics(batch_df):

    batch_text = "\n\n".join(
        f"[{row['chunk_id']}]\n{row['text']}"
        for _, row in batch_df.iterrows()
    )

    prompt = f"""
Analyze this MIT Deep Learning lecture transcript.

Identify the major learning topics.

Rules:
- Use only information from the transcript.
- Identify meaningful topics, not tiny details.
- A topic should support multiple quiz questions.
- Return ONLY valid JSON.

Format:
{{
  "topics": [
    {{
      "topic": "topic name",
      "description": "short description"
    }}
  ]
}}

Transcript:
{batch_text}
"""

    result = generate_json_with_retry(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    return result


# ============================================
# STEP 10 — EXTRACT TOPICS FROM ALL BATCHES
# ============================================

all_batch_topics = []

for i, batch in enumerate(batches, start=1):
    print(f"Processing batch {i}/{len(batches)}...")

    topics = extract_topics(batch)

    all_batch_topics.append(topics)

print("\nTopic extraction completed.")


# STEP 11 — CONSOLIDATE INTO EXACTLY 4 TOPICS

all_topics_text = json.dumps(
    all_batch_topics,
    indent=2
)

consolidation_prompt = f"""
You are an expert curriculum designer.

Below are topics extracted from different batches
of the same MIT Deep Learning lecture.

Your task is to consolidate them into EXACTLY 4
major learning topics.

Rules:
- Use ONLY the information present in the extracted topics.
- Merge overlapping or closely related topics.
- Do not invent new topics.
- Each final topic must be broad enough to support
  multiple high-quality quiz questions.
- Avoid administrative topics when possible unless
  they are genuinely important learning content.
- Keep the topic names concise.
- Provide a short description for each topic.
- Return ONLY valid JSON.

Required format:

{{
  "topics": [
    {{
      "topic": "Topic 1",
      "description": "Description"
    }},
    {{
      "topic": "Topic 2",
      "description": "Description"
    }},
    {{
      "topic": "Topic 3",
      "description": "Description"
    }},
    {{
      "topic": "Topic 4",
      "description": "Description"
    }}
  ]
}}

Extracted topics:
{all_topics_text}
"""

response = generate_with_retry(
    model="gemini-3.5-flash-lite",
    contents=consolidation_prompt,
    config={
        "response_mime_type": "application/json"
    }
)

major_topics = json.loads(response.text)

print(json.dumps(major_topics, indent=2))


# STEP 13 — ASSIGN ONE PRIMARY TOPIC PER CHUNK

topics_for_mapping = json.dumps(
    major_topics["topics"],
    indent=2
)

def assign_primary_topics(batch_df):

    batch_text = "\n\n".join(
        f"[{row['chunk_id']}]\n{row['text']}"
        for _, row in batch_df.iterrows()
    )

    prompt = f"""
You are classifying MIT Deep Learning lecture transcript chunks.

Choose EXACTLY ONE primary topic for each chunk from the
4 topics below.

Topics:
{topics_for_mapping}

Transcript chunks:
{batch_text}

Rules:
1. Every chunk must receive exactly ONE topic.
2. Choose the topic that represents the MAIN concept taught
   in that chunk.
3. Do not assign multiple topics.
4. Do not invent or rename topics.
5. Do not choose a topic just because it is briefly mentioned.
6. Consider the overall meaning of the chunk.
7. Return valid JSON only.

Format:

{{
  "chunk_topic_mapping": [
    {{
      "chunk_id": "...",
      "primary_topic": "..."
    }}
  ]
}}
"""

    response = generate_with_retry(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    return json.loads(response.text)


print("Primary topic mapping function ready")


# STEP 12 — MAP ALL CHUNKS TO PRIMARY TOPICS

all_mappings = []

for i, batch in enumerate(batches, start=1):

    print(f"Mapping batch {i}/{len(batches)}...")

    mapping = assign_primary_topics(batch)

    all_mappings.extend(
        mapping["chunk_topic_mapping"]
    )

print("\nTopic mapping completed.")
print("Total mappings:", len(all_mappings))


# ============================================
# STEP 13 — ADD PRIMARY TOPIC TO CHUNKS
# ============================================

mapping_df = pd.DataFrame(all_mappings)

print("Mapping rows:", len(mapping_df))
print(mapping_df.head())

chunks_df = chunks_df.merge(
    mapping_df,
    on="chunk_id",
    how="left"
)

print("\nTotal chunks:", len(chunks_df))
print(
    "Missing primary topics:",
    chunks_df["primary_topic"].isna().sum()
)

display(
    chunks_df[
        ["chunk_id", "primary_topic", "text"]
    ].head()
)


# STEP 14 — CHECK TOPIC DISTRIBUTION

topic_distribution = (
    chunks_df["primary_topic"]
    .value_counts()
    .rename_axis("topic")
    .reset_index(name="chunk_count")
)

display(topic_distribution)


# STEP 15 — GROUP CHUNKS BY TOPIC

topic_chunks = {
    topic: group.copy()
    for topic, group in chunks_df.groupby("primary_topic")
}

for topic, group in topic_chunks.items():
    print(f"\n{topic}")
    print(f"Chunks: {len(group)}")


# STEP 16 — GENERATE QUIZ

def generate_quiz(topic_name, source_text, num_questions=5):

    prompt = f"""
You are creating assessment questions for an MIT Deep Learning course.

Topic:
{topic_name}

Generate exactly {num_questions} high-quality multiple-choice questions
based ONLY on the transcript provided below.

Requirements:
1. Each question must be answerable from the transcript.
2. Create exactly 4 options: A, B, C, D.
3. Only ONE option must be correct.
4. Avoid duplicate or nearly identical questions.
5. Mix conceptual, factual, and application/understanding questions.
6. Include easy, medium, and hard questions where appropriate.
7. Wrong options should be plausible but incorrect based on the transcript.
8. Do not use outside knowledge.
9. Provide a concise explanation.
10. Return ONLY valid JSON.
11. Every question must primarily test the specified topic.
12. Use transcript chunks as evidence.
13. assessment_location must be a non-empty list of the exact
    chunk_id(s) supporting the question.
14. alignment_score must be a number from 1 to 5.
15. question_type must be one of:
    conceptual, factual, application.

Required JSON format:

{{
  "questions": [
    {{
      "question_text": "...",
      "answer_patterns": {{
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      }},
      "difficulty_signals": "easy",
      "concept_tags": ["..."],
      "correct_answer": "A",
      "assessment_location": ["chunk_id"],
      "alignment_score": 5,
      "question_type": "conceptual",
      "explanation": "..."
    }}
  ]
}}

Topic:
{topic_name}

Transcript:
{source_text}
"""

    response = generate_json_with_retry(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "max_output_tokens": 4096
        }
    )

    return response

# STEP 17 — QUIZ VALIDATION

def validate_quiz(topic_name, questions):

    validated_questions = []

    required_fields = [
        "question_text",
        "answer_patterns",
        "difficulty_signals",
        "concept_tags",
        "correct_answer",
        "assessment_location",
        "alignment_score",
        "question_type",
        "explanation"
    ]

    for i, q in enumerate(questions, start=1):

        issues = []

        # Required fields
        for field in required_fields:
            if field not in q:
                issues.append(f"Missing field: {field}")

        if issues:
            validated_questions.append({
                "question_index": i,
                "status": "rejected",
                "issues": issues
            })
            continue

        # Exactly 4 options
        options = q["answer_patterns"]

        if not isinstance(options, dict) or set(options.keys()) != {
            "A", "B", "C", "D"
        }:
            issues.append("Must have exactly A, B, C, D options")

        # Correct answer
        if q["correct_answer"] not in ["A", "B", "C", "D"]:
            issues.append("Invalid correct_answer")

        # Assessment location
        if (
            not isinstance(q["assessment_location"], list)
            or len(q["assessment_location"]) == 0
        ):
            issues.append("Missing assessment_location")

        # Alignment score: 1–5
        try:
            alignment = float(q["alignment_score"])

            if alignment < 1 or alignment > 5:
                issues.append(
                    "alignment_score must be between 1 and 5"
                )

        except (TypeError, ValueError):
            issues.append("Invalid alignment_score")

        # Question type
        if q["question_type"] not in [
            "conceptual",
            "factual",
            "application"
        ]:
            issues.append("Invalid question_type")

        status = "approved" if not issues else "rejected"

        validated_questions.append({
            "question_index": i,
            "status": status,
            "issues": issues
        })

    return {
        "topic": topic_name,
        "total_questions": len(questions),
        "approved": sum(
            x["status"] == "approved"
            for x in validated_questions
        ),
        "rejected": sum(
            x["status"] == "rejected"
            for x in validated_questions
        ),
        "validated_questions": validated_questions
    }


print("Quiz validator updated — alignment score: 1–5")


# Step - 18 VALIDATE TEST QUIZ
validation_result = validate_quiz(
    topic_name=topic,
    questions=test_quiz["questions"]
)

print(json.dumps(
    validation_result,
    indent=2
))


# STEP 19 — GENERATE QUIZ FOR ALL 4 TOPICS

all_quiz_questions = []

for topic_name, topic_df in topic_chunks.items():

    print(f"\nGenerating questions for: {topic_name}")
    print(f"Chunks: {len(topic_df)}")

    topic_text = "\n\n".join(
        f"CHUNK ID: {row['chunk_id']}\n"
        f"TIMESTAMP: {row['start_time']} → {row['end_time']}\n"
        f"CONTENT: {row['text']}"
        for _, row in topic_df.iterrows()
    )

    result = generate_quiz(
        topic_name=topic_name,
        source_text=topic_text,
        num_questions=5
    )

    all_quiz_questions.extend(
        result["questions"]
    )

    print(
        f"Generated: {len(result['questions'])}"
    )

print("\n" + "=" * 50)
print("QUIZ GENERATION COMPLETED")
print("=" * 50)
print("Total questions:", len(all_quiz_questions))


# STEP 20 — VALIDATE ALL 20 QUESTIONS

final_validation = validate_quiz(
    topic_name="lec01",
    questions=all_quiz_questions
)

print(json.dumps(final_validation, indent=2))


# STEP 21 — ALL 24 LECTURES SETUP

PROJECT_PATH = Path(r"D:\COURSE ERA PROJECT")

CHUNKS_DIR = (
    PROJECT_PATH
    / "03_PREPROCESSED_DATA"
    / "chunks"
)

QUIZ_DIR = (
    PROJECT_PATH
    / "04_SYNTHETIC_DATA"
    / "quiz"
)

QUIZ_DIR.mkdir(
    parents=True,
    exist_ok=True
)

chunk_files = sorted(
    CHUNKS_DIR.glob("lec*_caption_chunks.csv")
)

print("Chunk files found:", len(chunk_files))

for file in chunk_files:
    print(file.name)


# STEP 22 — LOAD ALL 24 LECTURE CHUNKS

all_lecture_chunks = {}

for chunk_file in chunk_files:

    lecture_id = chunk_file.stem.split("_")[0]

    df = pd.read_csv(chunk_file)

    all_lecture_chunks[lecture_id] = df

    print(
        f"{lecture_id}: "
        f"{len(df)} chunks"
    )

print("\n" + "=" * 50)
print("ALL LECTURES LOADED")
print("=" * 50)

print("Lectures:", len(all_lecture_chunks))
print(
    "Total chunks:",
    sum(len(df) for df in all_lecture_chunks.values())
)


# STEP 23 — REUSABLE LECTURE QUIZ PIPELINE

def process_lecture_quiz(
    lecture_id,
    chunks_df
):

    print("\n" + "=" * 60)
    print(f"PROCESSING {lecture_id}")
    print("=" * 60)

    chunks_df = chunks_df.copy()

    # --------------------------------------------------------
    # 1. Validate input columns
    # --------------------------------------------------------

    required_columns = [
        "chunk_id",
        "start_time",
        "end_time",
        "text"
    ]

    for col in required_columns:
        if col not in chunks_df.columns:
            raise ValueError(
                f"{lecture_id}: Missing column '{col}'"
            )

    # --------------------------------------------------------
    # 2. Create batches
    # --------------------------------------------------------

    batch_size = 10

    batches = [
        chunks_df.iloc[i:i + batch_size]
        for i in range(0, len(chunks_df), batch_size)
    ]

    # --------------------------------------------------------
    # 3. Extract topics
    # --------------------------------------------------------

    all_batch_topics = []

    for i, batch in enumerate(batches, start=1):

        print(
            f"Extracting topics: "
            f"batch {i}/{len(batches)}"
        )

        result = extract_topics(batch)

        if "topics" not in result:
            raise ValueError(
                f"{lecture_id}: "
                f"Topic extraction returned no 'topics'."
            )

        all_batch_topics.append(result)

    # --------------------------------------------------------
    # 4. Consolidate EXACTLY 4 major topics
    # --------------------------------------------------------

    all_topics_text = json.dumps(
        all_batch_topics,
        indent=2,
        ensure_ascii=False
    )

    consolidation_prompt = f"""
You are an expert curriculum designer.

Below are topics extracted from different batches
of the same MIT Deep Learning lecture.

Consolidate them into EXACTLY 4 major learning topics.

STRICT RULES:
- Return exactly 4 topics.
- Use ONLY information present in the extracted topics.
- Merge overlapping topics.
- Do not invent new concepts.
- Keep topic names concise.
- Each topic must be broad enough for multiple quiz questions.
- Return ONLY valid JSON.

Required format:

{{
  "topics": [
    {{
      "topic": "...",
      "description": "..."
    }},
    {{
      "topic": "...",
      "description": "..."
    }},
    {{
      "topic": "...",
      "description": "..."
    }},
    {{
      "topic": "...",
      "description": "..."
    }}
  ]
}}

Extracted topics:

{all_topics_text}
"""

    major_topics = generate_json_with_retry(
        model="gemini-3.5-flash-lite",
        contents=consolidation_prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    if "topics" not in major_topics:
        raise ValueError(
            f"{lecture_id}: Missing 'topics' in consolidation."
        )

    if len(major_topics["topics"]) != 4:
        raise ValueError(
            f"{lecture_id}: Expected exactly 4 topics, "
            f"got {len(major_topics['topics'])}"
        )

    topic_names = [
        topic["topic"].strip()
        for topic in major_topics["topics"]
    ]

    if len(set(topic_names)) != 4:
        raise ValueError(
            f"{lecture_id}: Duplicate major topics returned."
        )

    print(
        f"\nTopics: {len(topic_names)}"
    )

    for topic in topic_names:
        print(f"- {topic}")

    # --------------------------------------------------------
    # 5. Map every chunk to EXACTLY one approved topic
    # --------------------------------------------------------

    all_mappings = []

    topics_for_mapping = json.dumps(
        major_topics["topics"],
        indent=2,
        ensure_ascii=False
    )

    valid_topics = set(topic_names)

    for i, batch in enumerate(batches, start=1):

        print(
            f"Mapping topics: "
            f"batch {i}/{len(batches)}"
        )

        batch_text = "\n\n".join(
            f"CHUNK ID: {row['chunk_id']}\n"
            f"CONTENT: {row['text']}"
            for _, row in batch.iterrows()
        )

        mapping_prompt = f"""
You are classifying MIT Deep Learning lecture transcript chunks.

Assign EXACTLY ONE primary topic to EVERY chunk.

APPROVED TOPICS:

{topics_for_mapping}

STRICT RULES:
1. primary_topic MUST be copied EXACTLY from one of the
   approved topic names above.
2. Do NOT rename a topic.
3. Do NOT shorten a topic.
4. Do NOT create a new topic.
5. Every chunk_id must appear exactly once.
6. Return ONLY valid JSON.

Transcript chunks:

{batch_text}

Required format:

{{
  "chunk_topic_mapping": [
    {{
      "chunk_id": "...",
      "primary_topic": "EXACT APPROVED TOPIC"
    }}
  ]
}}
"""

        mapping_success = False
        mapping_result = None

        for attempt in range(3):

            try:

                mapping_result = generate_json_with_retry(
                    model="gemini-3.5-flash-lite",
                    contents=mapping_prompt,
                    config={
                        "response_mime_type": "application/json"
                    }
                )

                mapping_rows = mapping_result[
                    "chunk_topic_mapping"
                ]

                expected_chunk_ids = set(
                    batch["chunk_id"].tolist()
                )

                returned_chunk_ids = [
                    item["chunk_id"]
                    for item in mapping_rows
                ]

                returned_topics = [
                    item["primary_topic"].strip()
                    for item in mapping_rows
                ]

                # Exact chunk coverage
                if (
                    len(returned_chunk_ids)
                    != len(expected_chunk_ids)
                    or set(returned_chunk_ids)
                    != expected_chunk_ids
                    or len(returned_chunk_ids)
                    != len(set(returned_chunk_ids))
                ):
                    raise ValueError(
                        "Invalid chunk mapping."
                    )

                # Exact topic validation
                invalid_topics = [
                    topic
                    for topic in returned_topics
                    if topic not in valid_topics
                ]

                if invalid_topics:
                    raise ValueError(
                        f"Invalid topics returned: "
                        f"{invalid_topics}"
                    )

                mapping_success = True
                break

            except Exception as e:

                print(
                    f"Mapping retry "
                    f"{attempt + 1}/3: {e}"
                )

                if attempt == 2:
                    raise ValueError(
                        f"{lecture_id}: "
                        f"Topic mapping failed after 3 attempts "
                        f"for batch {i}."
                    )

        all_mappings.extend(
            mapping_rows
        )

    # --------------------------------------------------------
    # 6. Apply mapping
    # --------------------------------------------------------

    mapping_df = pd.DataFrame(
        all_mappings
    )

    chunks_df = chunks_df.merge(
        mapping_df,
        on="chunk_id",
        how="left"
    )

    if chunks_df["primary_topic"].isna().any():

        missing_chunks = chunks_df.loc[
            chunks_df["primary_topic"].isna(),
            "chunk_id"
        ].tolist()

        raise ValueError(
            f"{lecture_id}: Missing topic mapping for "
            f"{missing_chunks}"
        )

    invalid_after_merge = set(
        chunks_df["primary_topic"]
    ) - valid_topics

    if invalid_after_merge:

        raise ValueError(
            f"{lecture_id}: Invalid topics after mapping: "
            f"{invalid_after_merge}"
        )

    # --------------------------------------------------------
    # 7. Group by topic
    # --------------------------------------------------------

    topic_chunks = {
        topic: group.copy()
        for topic, group
        in chunks_df.groupby("primary_topic")
    }

    if len(topic_chunks) != 4:

        raise ValueError(
            f"{lecture_id}: Expected 4 topic groups, "
            f"got {len(topic_chunks)}"
        )

    # --------------------------------------------------------
    # 8. Generate 5 questions per topic
    # --------------------------------------------------------

    all_quiz_questions = []

    for topic_name in topic_names:

        topic_df = topic_chunks[topic_name]

        print(
            f"Generating quiz: "
            f"{topic_name} | "
            f"{len(topic_df)} chunks"
        )

        topic_text = "\n\n".join(
            f"CHUNK ID: {row['chunk_id']}\n"
            f"TIMESTAMP: "
            f"{row['start_time']} → {row['end_time']}\n"
            f"CONTENT: {row['text']}"
            for _, row in topic_df.iterrows()
        )

        generated = None

        for attempt in range(3):

            result = generate_quiz(
                topic_name=topic_name,
                source_text=topic_text,
                num_questions=5
            )

            questions = result.get(
                "questions",
                []
            )

            if len(questions) != 5:

                print(
                    f"Quiz retry "
                    f"{attempt + 1}/3: "
                    f"expected 5 questions, "
                    f"got {len(questions)}"
                )

                continue

            # Check assessment_location
            valid_locations = True

            allowed_chunk_ids = set(
                topic_df["chunk_id"].tolist()
            )

            for question in questions:

                location = question.get(
                    "assessment_location"
                )

                if (
                    not isinstance(location, list)
                    or len(location) == 0
                    or not set(location).issubset(
                        allowed_chunk_ids
                    )
                ):

                    valid_locations = False
                    break

            if valid_locations:

                generated = questions
                break

            print(
                f"Quiz retry "
                f"{attempt + 1}/3: "
                f"invalid assessment_location"
            )

        if generated is None:

            raise ValueError(
                f"{lecture_id}: "
                f"Topic '{topic_name}' failed to "
                f"generate 5 valid questions after 3 attempts."
            )

        all_quiz_questions.extend(
            generated
        )

    # --------------------------------------------------------
    # 9. Final question count
    # --------------------------------------------------------

    if len(all_quiz_questions) != 20:

        raise ValueError(
            f"{lecture_id}: Expected 20 questions, "
            f"got {len(all_quiz_questions)}"
        )

    # --------------------------------------------------------
    # 10. Assign exact topic to each question
    # --------------------------------------------------------

    question_index = 0

    for topic_name in topic_names:

        for _ in range(5):

            all_quiz_questions[
                question_index
            ]["topic"] = topic_name

            question_index += 1

    # --------------------------------------------------------
    # 11. Validate assessment locations
    # --------------------------------------------------------

    for i, question in enumerate(
        all_quiz_questions,
        start=1
    ):

        location = question.get(
            "assessment_location"
        )

        if (
            not isinstance(location, list)
            or len(location) == 0
        ):

            raise ValueError(
                f"{lecture_id}: "
                f"Question {i} has invalid "
                f"assessment_location."
            )

    # --------------------------------------------------------
    # 12. Validate complete quiz
    # --------------------------------------------------------

    print(
        "\nValidating quiz..."
    )

    validation = validate_quiz(
        topic_name=lecture_id,
        questions=all_quiz_questions
    )

    approved = validation[
        "approved"
    ]

    rejected = validation[
        "rejected"
    ]

    print(
        f"Approved: {approved}"
    )

    print(
        f"Rejected: {rejected}"
    )

    # --------------------------------------------------------
    # 13. Final validation gate
    # --------------------------------------------------------

    if approved != 20 or rejected != 0:

        raise ValueError(
            f"{lecture_id}: "
            f"Quiz validation failed. "
            f"Approved={approved}, "
            f"Rejected={rejected}"
        )

    # --------------------------------------------------------
    # 14. Return final result
    # --------------------------------------------------------

    result = {
        "lecture_id": lecture_id,
        "major_topics": major_topics,
        "questions": all_quiz_questions,
        "validation": validation,
        "chunks": chunks_df
    }

    print(
        f"\n{lecture_id}: "
        f"20 questions generated and approved."
    )

    return result


print(
    "Reusable lecture quiz pipeline ready."
)


# STEP 24 — PROCESS ALL LECTURES

all_results = {}
failed_lectures = []

for lecture_id in sorted(all_lecture_chunks.keys()):

    print("\n" + "=" * 60)
    print(f"STARTING {lecture_id}")
    print("=" * 60)

    try:

        result = process_lecture_quiz(
            lecture_id=lecture_id,
            chunks_df=all_lecture_chunks[lecture_id]
        )

        all_results[lecture_id] = result

        print(f"\n{lecture_id} SUCCESS")
        print(
            "Questions:",
            len(result["questions"])
        )
        print(
            "Approved:",
            result["validation"]["approved"]
        )
        print(
            "Rejected:",
            result["validation"]["rejected"]
        )

    except Exception as e:

        failed_lectures.append({
            "lecture_id": lecture_id,
            "error_type": type(e).__name__,
            "error": str(e)
        })

        print(
            f"\n{lecture_id} FAILED: "
            f"{type(e).__name__} — {e}"
        )

print("\n" + "=" * 60)
print("ALL LECTURES PROCESSING COMPLETED")
print("=" * 60)

print(
    "Successful lectures:",
    len(all_results)
)

print(
    "Failed lectures:",
    len(failed_lectures)
)

if failed_lectures:

    print("\nFailed lectures:")

    for failure in failed_lectures:
        print(
            f"{failure['lecture_id']}: "
            f"{failure['error_type']} — "
            f"{failure['error']}"
        )


# STEP 25 — CHECK FAILED LECTURES

print("Successful lectures:")
print(sorted(all_results.keys()))

print("\nFailed lectures:")

for failure in failed_lectures:
    print(
        f"{failure['lecture_id']}: "
        f"{failure['error_type']} — "
        f"{failure['error']}"
    )

print("\nFailed lecture IDs:")

failed_ids = [
    failure["lecture_id"]
    for failure in failed_lectures
]

print(failed_ids)



# STEP 26 — SAVE LEC23 + LEC24 JSON FILES


for lecture_id in ["lec23", "lec24"]:

    if lecture_id not in all_results:
        raise ValueError(
            f"{lecture_id} not found in all_results"
        )

    result = all_results[lecture_id]

    questions = result["questions"]

    if len(questions) != 20:
        raise ValueError(
            f"{lecture_id}: expected 20 questions, "
            f"found {len(questions)}"
        )

    lecture_dir = QUIZ_DIR / lecture_id
    lecture_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    quiz_file = (
        lecture_dir
        / f"{lecture_id}_quiz.json"
    )

    with open(
        quiz_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "lecture_id": lecture_id,
                "total_questions": 20,
                "topics": result.get(
                    "major_topics",
                    []
                ),
                "questions": questions
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"{lecture_id}: SAVED → {quiz_file}"
    )
    print(
        f"Questions: {len(questions)}"
    )

print("\n" + "=" * 60)
print("LEC23 + LEC24 JSON FILES SAVED SUCCESSFULLY")
print("=" * 60)


# Initialize results container after kernel restart
all_results = {}

print("all_results initialized.")


# STEP 27 — VERIFY ALL 24 QUIZ JSON FILES

print("=" * 60)
print("VERIFYING ALL 24 LECTURE QUIZ FILES")
print("=" * 60)

missing_files = []
invalid_files = []
lecture_question_counts = {}

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    # Check file exists
    if not quiz_file.exists():

        missing_files.append(lecture_id)

        print(f"{lecture_id}: ❌ FILE NOT FOUND")
        continue

    try:

        with open(
            quiz_file,
            "r",
            encoding="utf-8"
        ) as f:

            quiz_data = json.load(f)

        questions = quiz_data.get(
            "questions",
            []
        )

        # Check exactly 20 questions
        if len(questions) != 20:

            invalid_files.append(
                (lecture_id, len(questions))
            )

            print(
                f"{lecture_id}: ❌ "
                f"{len(questions)} questions"
            )

            continue

        lecture_question_counts[
            lecture_id
        ] = len(questions)

        print(
            f"{lecture_id}: ✅ "
            f"20 questions"
        )

    except Exception as e:

        invalid_files.append(
            (lecture_id, str(e))
        )

        print(
            f"{lecture_id}: ❌ "
            f"{type(e).__name__}: {e}"
        )


# --------------------------------------------
# FINAL VERIFICATION
# --------------------------------------------

total_questions = sum(
    lecture_question_counts.values()
)

print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)

print(
    "Files verified:",
    len(lecture_question_counts)
)

print(
    "Missing files:",
    len(missing_files)
)

print(
    "Invalid files:",
    len(invalid_files)
)

print(
    "Total questions:",
    total_questions
)


# --------------------------------------------
# Safety checks
# --------------------------------------------

assert len(missing_files) == 0, (
    f"Missing lecture files: {missing_files}"
)

assert len(invalid_files) == 0, (
    f"Invalid lecture files: {invalid_files}"
)

assert len(lecture_question_counts) == 24

assert total_questions == 480


print("\n" + "=" * 60)
print("SUCCESS — ALL 24 QUIZ JSON FILES VERIFIED")
print("TOTAL QUESTIONS: 480")
print("=" * 60)


# STEP 28 — LOAD ALL QUIZ JSON FILES

all_quiz_data = {}

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(
        quiz_file,
        "r",
        encoding="utf-8"
    ) as f:

        quiz_data = json.load(f)

    all_quiz_data[lecture_id] = quiz_data

    print(
        f"{lecture_id}: "
        f"{len(quiz_data['questions'])} questions loaded"
    )


# --------------------------------------------
# Final check
# --------------------------------------------

total_questions = sum(
    len(data["questions"])
    for data in all_quiz_data.values()
)

print("\n" + "=" * 60)
print("ALL QUIZ DATA LOADED")
print("=" * 60)

print("Lectures:", len(all_quiz_data))
print("Total questions:", total_questions)

assert len(all_quiz_data) == 24
assert total_questions == 480

print("\nSUCCESS — 24 lectures and 480 questions loaded.")

# # ============================================================
# # QUIZ DATABASE — MASTER VALIDATION & EXPORT
# # ============================================================

#  BUILD FINAL QUIZ DATABASE DATAFRAME

all_quiz_records = []

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(quiz_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for question in data["questions"]:
        all_quiz_records.append(question)


quiz_df = pd.DataFrame(all_quiz_records)

print("Total questions:", len(quiz_df))
print("Columns:", len(quiz_df.columns))
print("\nColumns:")
print(quiz_df.columns.tolist())

## step 1
print(quiz_df.columns.tolist())

display(
    quiz_df[
        [
            "record_id",
            "course_id",
            "module_id",
            "lecture_id",
            "quiz_id",
            "question_id"
        ]
    ].head(10)
)


# STEP 2 — CREATE UNIQUE QUIZ RECORD IDs

quiz_df["record_id"] = (
    quiz_df["lecture_id"]
    + "_quiz_"
    + quiz_df.groupby("lecture_id").cumcount().add(1).astype(str).str.zfill(3)
)

print("Total records:", len(quiz_df))
print("Unique record IDs:", quiz_df["record_id"].nunique())

display(
    quiz_df[
        ["record_id", "lecture_id", "quiz_id", "question_id"]
    ].head(10)
)


# STEP 3 — ALIGN SHARED IDs

quiz_df["course_id"] = "deeplearning"

quiz_df["module_id"] = (
    "MOD_" +
    quiz_df["lecture_id"]
    .str.replace("lec", "", regex=False)
    .str.zfill(2)
)

print("Shared IDs updated.")

display(
    quiz_df[
        ["course_id", "module_id", "lecture_id", "record_id"]
    ].head(10)
)


# STEP 4 — VERIFY ALL LECTURE ID MAPPINGS

id_check = (
    quiz_df[
        ["course_id", "module_id", "lecture_id"]
    ]
    .drop_duplicates()
    .sort_values("lecture_id")
    .reset_index(drop=True)
)

display(id_check)

print("Total lecture mappings:", len(id_check))


# STEP 5 — CHECK CURRENT QUIZ SCHEMA

print(quiz_df.columns.tolist())

print("\nRows:", len(quiz_df))
print("Columns:", len(quiz_df.columns))


# STEP 6 — CHECK FOR BLANK VALUES

print(quiz_df.isna().sum())

print("\nBlank strings:")
print(
    (quiz_df == "").sum()
)


# STEP 7 — CHECK DATA TYPES

print(quiz_df.dtypes)


# STEP 8 — CHECK QUESTION ID UNIQUENESS

print("Total questions:", len(quiz_df))
print("Unique question IDs:", quiz_df["question_id"].nunique())
print("Unique record IDs:", quiz_df["record_id"].nunique())


# STEP 9 — VERIFY SHARED ID CONSISTENCY

id_consistency = (
    quiz_df[
        ["course_id", "module_id", "lecture_id"]
    ]
    .drop_duplicates()
)

print("Unique course/module/lecture combinations:",
      len(id_consistency))

print("\nExpected: 24")


# STEP 10 — INSPECT ONE COMPLETE RECORD

display(
    quiz_df.iloc[0].to_frame(name="value")
)


# ============================================================
# STEP 11 — SAVE FINAL QUIZ MASTER JSON
# ============================================================

master_database_file = (
    QUIZ_DIR.parent
    / "database"
    / "master_quiz_database.json"
)

master_database = {
    "dataset_name": "MIT Deep Learning Quiz Database",
    "total_lectures": 24,
    "total_questions": len(quiz_df),
    "questions": quiz_df.to_dict(orient="records")
}

with open(
    master_database_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        master_database,
        f,
        indent=2,
        ensure_ascii=False
    )

print("MASTER JSON SAVED")
print("Path:", master_database_file)
print("Questions:", len(master_database["questions"]))


# ============================================================
# STEP 12 — SAVE FINAL QUIZ MASTER CSV
# ============================================================

master_csv_file = (
    QUIZ_DIR.parent
    / "database"
    / "master_quiz_database.csv"
)

quiz_df.to_csv(
    master_csv_file,
    index=False,
    encoding="utf-8"
)

print("MASTER CSV SAVED")
print("Path:", master_csv_file)
print("Rows:", len(quiz_df))
print("Columns:", len(quiz_df.columns))


# ============================================================
# STEP 13 — FINAL QUIZ DATABASE VALIDATION
# ============================================================

required_fields = [
    "record_id",
    "course_id",
    "module_id",
    "lecture_id",
    "quiz_id",
    "question_id",
    "question",
    "options",
    "correct_answer",
    "explanation",
    "topic",
    "source_file"
]

print("Total questions:", len(quiz_df))

print("Unique record IDs:", quiz_df["record_id"].nunique())
print("Unique question IDs:", quiz_df["question_id"].nunique())

print(
    "Unique course/module/lecture combinations:",
    quiz_df[
        ["course_id", "module_id", "lecture_id"]
    ].drop_duplicates().shape[0]
)

print("Expected combinations: 24")

# Required fields
blank_counts = quiz_df[required_fields].isna().sum()
blank_fields = blank_counts[blank_counts > 0]

print("Fields with blank values:", len(blank_fields))

# ID convention
bad_record_ids = quiz_df[
    ~quiz_df["record_id"].str.match(
        r"^lec\d{2}_quiz_\d{3}$"
    )
]

print("Invalid record IDs:", len(bad_record_ids))

if (
    len(quiz_df) == 480
    and quiz_df["record_id"].nunique() == 480
    and quiz_df["question_id"].nunique() == 480
    and quiz_df[
        ["course_id", "module_id", "lecture_id"]
    ].drop_duplicates().shape[0] == 24
    and len(blank_fields) == 0
    and len(bad_record_ids) == 0
):
    print("\nSUCCESS — FINAL QUIZ DATABASE VALIDATION PASSED")
else:
    print("\nCHECK FAILED — REVIEW THE RESULTS ABOVE")

# # ============================================================
# # INDIVIDUAL QUIZ JSON — STANDARDIZATION & CSV BACKUP
# # ============================================================

# STEP 1 — INSPECT INDIVIDUAL QUIZ JSON

import json

quiz_file = (
    QUIZ_DIR
    / "lec01"
    / "lec01_quiz.json"
)

with open(quiz_file, "r", encoding="utf-8") as f:
    lec01_data = json.load(f)

print("Total questions:", len(lec01_data["questions"]))

print("\nFirst question:")
print(json.dumps(
    lec01_data["questions"][0],
    indent=2,
    ensure_ascii=False
))


# STEP 2 — CHECK ALL INDIVIDUAL QUIZ JSON SCHEMAS

import json

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(quiz_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    fields = list(data["questions"][0].keys())

    print(lecture_id, "→", fields)


# STEP 3 — COMPARE SOURCE FIELDS WITH FINAL DATABASE FIELDS

source_fields = set(lec01_data["questions"][0].keys())

database_fields = set(quiz_df.columns)

print("SOURCE-ONLY FIELDS:")
print(sorted(source_fields - database_fields))

print("\nDATABASE-ONLY FIELDS:")
print(sorted(database_fields - source_fields))


# STEP 4 — BUILD DATABASE-READY lec01 IN MEMORY

import json

lecture_id = "lec01"

quiz_file = (
    QUIZ_DIR
    / lecture_id
    / f"{lecture_id}_quiz.json"
)

with open(quiz_file, "r", encoding="utf-8") as f:
    data = json.load(f)

transformed_questions = []

for i, q in enumerate(data["questions"], start=1):

    transformed_q = {
        # Database fields
        "record_id": f"{lecture_id}_quiz_{i:03d}",
        "course_id": "deeplearning",
        "module_id": f"MOD_{int(lecture_id.replace('lec', '')):02d}",
        "lecture_id": lecture_id,
        "quiz_id": f"quiz_{lecture_id}",
        "question_id": f"{lecture_id}_q{i:03d}",

        "question": q["question_text"],
        "options": json.dumps(
            q["answer_patterns"],
            ensure_ascii=False
        ),
        "correct_answer": q["correct_answer"],
        "explanation": q["explanation"],
        "topic": q["topic"],
        "source_file": f"{lecture_id}_quiz.json",

        # Preserve original generation metadata
        "difficulty_signals": q["difficulty_signals"],
        "concept_tags": q["concept_tags"],
        "assessment_location": q["assessment_location"],
        "alignment_score": q["alignment_score"],
        "question_type": q["question_type"],
    }

    transformed_questions.append(transformed_q)

# Inspect first transformed question
print(json.dumps(
    transformed_questions[0],
    indent=2,
    ensure_ascii=False
))


# STEP 5 — UPDATE ALL 24 INDIVIDUAL QUIZ JSON FILES

import json

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(quiz_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    transformed_questions = []

    for i, q in enumerate(data["questions"], start=1):

        transformed_q = {
            # Database fields
            "record_id": f"{lecture_id}_quiz_{i:03d}",
            "course_id": "deeplearning",
            "module_id": f"MOD_{lecture_num:02d}",
            "lecture_id": lecture_id,
            "quiz_id": f"quiz_{lecture_id}",
            "question_id": f"{lecture_id}_q{i:03d}",

            "question": q["question_text"],
            "options": q["answer_patterns"],
            "correct_answer": q["correct_answer"],
            "explanation": q["explanation"],
            "topic": q["topic"],
            "source_file": f"{lecture_id}_quiz.json",

            # Preserve original metadata
            "difficulty_signals": q["difficulty_signals"],
            "concept_tags": q["concept_tags"],
            "assessment_location": q["assessment_location"],
            "alignment_score": q["alignment_score"],
            "question_type": q["question_type"],
        }

        transformed_questions.append(transformed_q)

    # Update only this lecture's JSON
    data["questions"] = transformed_questions

    with open(quiz_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"{lecture_id} updated — {len(transformed_questions)} questions")

print("\nSUCCESS — ALL 24 INDIVIDUAL QUIZ JSON FILES UPDATED")


# STEP 6 — VERIFY ALL 24 INDIVIDUAL JSON FILES

import json

required_fields = [
    "record_id",
    "course_id",
    "module_id",
    "lecture_id",
    "quiz_id",
    "question_id",
    "question",
    "options",
    "correct_answer",
    "explanation",
    "topic",
    "source_file"
]

total_questions = 0
all_valid = True

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(quiz_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data["questions"]
    total_questions += len(questions)

    # Check schema
    fields = list(questions[0].keys())

    missing = [
        field for field in required_fields
        if field not in fields
    ]

    # Check IDs
    expected_module = f"MOD_{lecture_num:02d}"

    for i, q in enumerate(questions, start=1):

        expected_record = f"{lecture_id}_quiz_{i:03d}"
        expected_question = f"{lecture_id}_q{i:03d}"

        if (
            q["record_id"] != expected_record
            or q["course_id"] != "deeplearning"
            or q["module_id"] != expected_module
            or q["lecture_id"] != lecture_id
            or q["quiz_id"] != f"quiz_{lecture_id}"
            or q["question_id"] != expected_question
        ):
            all_valid = False

    if missing:
        all_valid = False
        print(f"{lecture_id} → MISSING:", missing)
    else:
        print(f"{lecture_id} → OK ({len(questions)} questions)")

print("\n" + "=" * 50)
print("TOTAL QUESTIONS:", total_questions)
print("ALL FILES VALID:", all_valid)


# STEP 7 — VERIFY ORIGINAL METADATA

metadata_fields = [
    "difficulty_signals",
    "concept_tags",
    "assessment_location",
    "alignment_score",
    "question_type"
]

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(quiz_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    missing = [
        field
        for field in metadata_fields
        if field not in data["questions"][0]
    ]

    if missing:
        print(f"{lecture_id} → MISSING: {missing}")
    else:
        print(f"{lecture_id} → metadata OK")

print("\nMetadata verification complete.")


# STEP 8 — CHECK MISSING VALUES IN ALL INDIVIDUAL JSON FILES

required_fields = [
    "record_id",
    "course_id",
    "module_id",
    "lecture_id",
    "quiz_id",
    "question_id",
    "question",
    "options",
    "correct_answer",
    "explanation",
    "topic",
    "source_file"
]

missing_count = 0

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(quiz_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, q in enumerate(data["questions"], start=1):

        for field in required_fields:

            value = q.get(field)

            if value is None or value == "":
                print(
                    f"{lecture_id}, question {i}: "
                    f"blank field → {field}"
                )
                missing_count += 1

print("\nTotal blank required fields:", missing_count)


# STEP 9 — CHECK ID UNIQUENESS ACROSS ALL 24 FILES

all_record_ids = []
all_question_ids = []

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    quiz_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    with open(quiz_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for q in data["questions"]:
        all_record_ids.append(q["record_id"])
        all_question_ids.append(q["question_id"])


print("Total records:", len(all_record_ids))
print("Unique record IDs:", len(set(all_record_ids)))

print("Total question IDs:", len(all_question_ids))
print("Unique question IDs:", len(set(all_question_ids)))

print("\nDuplicate record IDs:",
      len(all_record_ids) - len(set(all_record_ids)))

print("Duplicate question IDs:",
      len(all_question_ids) - len(set(all_question_ids)))


# STEP 10 — COMPARE INDIVIDUAL JSONs WITH MASTER CSV

import pandas as pd

master_csv_file = (
    QUIZ_DIR.parent
    / "database"
    / "master_quiz_database.csv"
)

master_df = pd.read_csv(master_csv_file)

individual_ids = set(all_record_ids)
master_ids = set(master_df["record_id"])

print("Individual JSON records:", len(individual_ids))
print("Master CSV records:", len(master_ids))

print("Missing from master:",
      len(individual_ids - master_ids))

print("Missing from individual JSONs:",
      len(master_ids - individual_ids))


# STEP 11 — CREATE CSV BACKUPS FOR ALL INDIVIDUAL QUIZ JSONs

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    json_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.json"
    )

    csv_file = (
        QUIZ_DIR
        / lecture_id
        / f"{lecture_id}_quiz.csv"
    )

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data["questions"])

    # Convert lists/dictionaries to JSON strings for CSV
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: json.dumps(x, ensure_ascii=False)
            if isinstance(x, (list, dict))
            else x
        )

    df.to_csv(
        csv_file,
        index=False,
        encoding="utf-8"
    )

    print(
        f"{lecture_id} → CSV backup created "
        f"({len(df)} questions)"
    )

print("\nSUCCESS — ALL 24 INDIVIDUAL QUIZ CSV BACKUPS CREATED")





