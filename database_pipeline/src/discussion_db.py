# ============================================
# STEP 1 — DISCUSSION / REVIEW PROJECT SETUP
# ============================================

import os
import json
import time
import pandas as pd
from pathlib import Path

print("Environment setup complete.")
print("Pandas version:", pd.__version__)

# ============================================
# STEP 2 — PROJECT PATHS
# ============================================

PROJECT_DIR = Path(r"D:\COURSE ERA PROJECT")

PREPROCESSED_DIR = (
    PROJECT_DIR
    / "03_PREPROCESSED_DATA"
)

CHUNKS_DIR = (
    PREPROCESSED_DIR
    / "Chunks"
)

SYNTHETIC_DIR = (
    PROJECT_DIR
    / "04_SYNTHETIC_DATA"
)

DISCUSSION_DIR = (
    SYNTHETIC_DIR
    / "discussion"
)

DATABASE_DIR = (
    DISCUSSION_DIR
    / "database"
)


# Create output directories
DISCUSSION_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Verify paths
print("Project:", PROJECT_DIR)
print("Chunks:", CHUNKS_DIR)
print("Discussion:", DISCUSSION_DIR)
print("Database:", DATABASE_DIR)

print("\nPath setup completed successfully.")

# ============================================
# STEP 3 — VERIFY ALL 24 LECTURE CHUNK FILES
# ============================================

chunk_files = sorted(
    CHUNKS_DIR.glob("lec*_caption_chunks.csv")
)

print("=" * 60)
print("VERIFYING LECTURE CHUNK FILES")
print("=" * 60)

print("Files found:", len(chunk_files))

for file in chunk_files:
    print(file.name)


# Safety check
assert len(chunk_files) == 24, (
    f"Expected 24 lecture files, found {len(chunk_files)}"
)

print("\nSUCCESS — ALL 24 LECTURE CHUNK FILES FOUND")

# ============================================
# STEP 4 — LOAD ALL 24 LECTURE CHUNKS
# ============================================

all_lecture_chunks = {}

for chunk_file in chunk_files:

    lecture_id = chunk_file.stem.split("_")[0]

    df = pd.read_csv(chunk_file)

    all_lecture_chunks[lecture_id] = df

    print(
        f"{lecture_id}: "
        f"{len(df)} chunks"
    )


print("\n" + "=" * 60)
print("ALL LECTURES LOADED")
print("=" * 60)

print(
    "Lectures:",
    len(all_lecture_chunks)
)

print(
    "Total chunks:",
    sum(
        len(df)
        for df in all_lecture_chunks.values()
    )
)

# Safety checks
assert len(all_lecture_chunks) == 24

assert all(
    lecture_id in all_lecture_chunks
    for lecture_id in [
        f"lec{i:02d}"
        for i in range(1, 25)
    ]
)

print("\nSUCCESS — ALL 24 LECTURES LOADED")

# ============================================
# STEP 5 — GEMINI API SETUP
# ============================================

from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Read API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Check your .env file."
    )

# Create Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)

print("Gemini API setup successful.")
print("Client initialized successfully.")

# ============================================
# STEP 6 — BUILD LECTURE SOURCE TEXT
# ============================================

lecture_sources = {}

required_columns = [
    "chunk_id",
    "start_time",
    "end_time",
    "text"
]

for lecture_id, df in all_lecture_chunks.items():

    # Check required columns
    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{lecture_id}: missing columns "
            f"{missing_columns}"
        )

    # Sort chronologically
    df = df.sort_values(
        "start_time"
    ).copy()

    # Build source text
    source_text = "\n\n".join(
        f"[CHUNK_ID: {row['chunk_id']}]\n"
        f"[TIME: {row['start_time']} - {row['end_time']}]\n\n"
        f"{row['text']}"
        for _, row in df.iterrows()
    )

    lecture_sources[lecture_id] = source_text

    print(
        f"{lecture_id}: "
        f"{len(df)} chunks | "
        f"{len(source_text.split())} words"
    )


print("\n" + "=" * 60)
print("LECTURE SOURCE TEXTS BUILT")
print("=" * 60)

print(
    "Lectures:",
    len(lecture_sources)
)

assert len(lecture_sources) == 24

print(
    "\nSUCCESS — ALL 24 LECTURE SOURCES READY"
)

# ============================================
# STEP 7 — DISCUSSION GENERATION FUNCTION
# ============================================

def generate_lecture_discussions(
    lecture_id,
    lecture_source,
    num_reviews=25
):

    prompt = f"""
You are generating synthetic learner discussions/reviews
for an educational course.

LECTURE ID:
{lecture_id}

LECTURE TRANSCRIPT:
{lecture_source}

Generate exactly {num_reviews} realistic learner
discussion/review records.

TARGET DISTRIBUTION:
- 8 Positive
- 4 Neutral
- 6 Confusion
- 5 Difficulty
- 2 Clarification

IMPORTANT RULES:

1. Every discussion MUST be grounded ONLY in the
   provided lecture transcript.

2. Do not invent concepts, examples, claims,
   chunk IDs, or timestamps.

3. Every discussion must relate to something
   actually taught in this lecture.

4. Use exact chunk_id values from the transcript.

5. Use the exact start_time and end_time values
   associated with those chunks.

6. A discussion may reference multiple chunks
   when appropriate.

7. Keep learner posts natural and realistic,
   generally 1–3 sentences.

8. Do not mention that the content is synthetic
   or AI-generated.

9. Avoid generic comments such as:
   "Great lecture" without lecture-specific content.

10. Positive discussions should mention something
    specific that helped the learner understand.

11. Neutral discussions should be factual or
    exploratory without strong positive or negative
    sentiment.

12. Confusion discussions should describe a genuine
    conceptual misunderstanding or uncertainty.

13. Difficulty discussions should describe a genuine
    learning challenge supported by the transcript.

14. Clarification discussions should ask a specific
    question about something actually explained
    in the lecture.

15. concept_tags must contain only concepts explicitly
    supported by the referenced transcript chunks.

16. recurring_theme should represent a meaningful
    learner discussion theme. Reuse meaningful themes
    when appropriate.

17. severity:
    Low = minor difficulty or curiosity
    Medium = meaningful confusion/difficulty
    High = major learning barrier

18. Return ONLY valid JSON.

19. Do not use markdown or JSON code fences.

20. Do not add any text before or after the JSON.

REQUIRED OUTPUT FORMAT:

{{
  "reviews": [
    {{
      "review_id": "REV_{lecture_id}_001",
      "lecture_id": "{lecture_id}",
      "chunk_ids": ["chunk_id"],
      "timestamps": [
        {{
          "start_time": "00:00:00.000",
          "end_time": "00:00:00.000"
        }}
      ],
      "review_text": "...",
      "sentiment": "Positive",
      "recurring_theme": "...",
      "concept_tags": ["..."],
      "friction_type": "Positive",
      "severity": "Low",
      "source": "synthetic_ai"
    }}
  ]
}}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.3
        }
    )

    raw_output = response.text.strip()

    if not raw_output:
        raise ValueError(
            f"{lecture_id}: Gemini returned empty response."
        )

    try:
        result = json.loads(raw_output)

    except json.JSONDecodeError as e:

        print("\nJSON parsing failed.")
        print("Lecture:", lecture_id)
        print("Error:", e)
        print("\nRAW RESPONSE:")
        print(raw_output)

        raise ValueError(
            f"{lecture_id}: Gemini returned invalid JSON."
        )

    return result


print("Discussion generation function ready.")


# ============================================
# STEP 9 — VALIDATE TEST DISCUSSIONS
# ============================================

reviews = test_result["reviews"]

print("=" * 60)
print("VALIDATING TEST DISCUSSIONS")
print("=" * 60)

# --------------------------------------------
# 1. Total count
# --------------------------------------------

assert len(reviews) == 25

print("Total reviews:", len(reviews))


# --------------------------------------------
# 2. Required fields
# --------------------------------------------

required_fields = [
    "review_id",
    "lecture_id",
    "chunk_ids",
    "timestamps",
    "review_text",
    "sentiment",
    "recurring_theme",
    "concept_tags",
    "friction_type",
    "severity",
    "source"
]

for review in reviews:

    missing = [
        field
        for field in required_fields
        if field not in review
    ]

    assert not missing, (
        f"{review.get('review_id')}: "
        f"missing fields {missing}"
    )


# --------------------------------------------
# 3. Lecture validation
# --------------------------------------------

assert all(
    review["lecture_id"] == "lec01"
    for review in reviews
)


# --------------------------------------------
# 4. Distribution validation
# --------------------------------------------

friction_counts = {}

for review in reviews:

    friction = review["friction_type"]

    friction_counts[friction] = (
        friction_counts.get(friction, 0) + 1
    )

print("\nFriction distribution:")

for friction, count in friction_counts.items():
    print(f"{friction}: {count}")


expected_distribution = {
    "Positive": 8,
    "Neutral": 4,
    "Confusion": 6,
    "Difficulty": 5,
    "Clarification": 2
}

assert friction_counts == expected_distribution


# --------------------------------------------
# 5. Source chunk validation
# --------------------------------------------

lecture_df = all_lecture_chunks["lec01"]

chunk_metadata = (
    lecture_df[
        ["chunk_id", "start_time", "end_time"]
    ]
    .drop_duplicates("chunk_id")
    .set_index("chunk_id")
)

valid_chunk_ids = set(chunk_metadata.index)

for review in reviews:

    assert isinstance(
        review["chunk_ids"],
        list
    )

    assert len(
        review["chunk_ids"]
    ) > 0

    for chunk_id in review["chunk_ids"]:

        assert chunk_id in valid_chunk_ids, (
            f"Invalid chunk ID: {chunk_id}"
        )


# --------------------------------------------
# 6. REBUILD TIMESTAMPS FROM SOURCE
# --------------------------------------------
#
# Gemini timestamps are NOT trusted.
# Source CSV is authoritative.
# --------------------------------------------

for review in reviews:

    review["timestamps"] = [
        {
            "start_time": chunk_metadata.loc[
                chunk_id,
                "start_time"
            ],
            "end_time": chunk_metadata.loc[
                chunk_id,
                "end_time"
            ]
        }
        for chunk_id in review["chunk_ids"]
    ]


# --------------------------------------------
# 7. Final timestamp verification
# --------------------------------------------

for review in reviews:

    assert len(
        review["chunk_ids"]
    ) == len(
        review["timestamps"]
    )

    for chunk_id, timestamp in zip(
        review["chunk_ids"],
        review["timestamps"]
    ):

        actual = chunk_metadata.loc[
            chunk_id
        ]

        assert (
            timestamp["start_time"]
            == actual["start_time"]
        )

        assert (
            timestamp["end_time"]
            == actual["end_time"]
        )


# --------------------------------------------
# SUCCESS
# --------------------------------------------

print("\n" + "=" * 60)
print("SUCCESS — TEST DISCUSSIONS VALIDATED")
print("=" * 60)

print("Reviews: 25")
print("Distribution: VALID")
print("Required fields: VALID")
print("Chunk IDs: VALID")
print("Timestamps: SOURCE-ACCURATE")


# ============================================
# STEP 10 — PRODUCTION DISCUSSION GENERATION
# ============================================

# --------------------------------------------
# Production generation + validation
# --------------------------------------------

def process_lecture_discussions(
    lecture_id,
    lecture_source,
    lecture_df,
    output_file
):

    print("\n" + "=" * 60)
    print(f"PROCESSING {lecture_id}")
    print("=" * 60)

    # ----------------------------------------
    # Generate
    # ----------------------------------------

    result = generate_lecture_discussions(
        lecture_id=lecture_id,
        lecture_source=lecture_source,
        num_reviews=25
    )

    reviews = result.get("reviews", [])

    # ----------------------------------------
    # Count validation
    # ----------------------------------------

    if len(reviews) != 25:
        raise ValueError(
            f"{lecture_id}: expected 25 reviews, "
            f"got {len(reviews)}"
        )

    # ----------------------------------------
    # Distribution validation
    # ----------------------------------------

    friction_counts = {}

    for review in reviews:

        friction = review["friction_type"]

        friction_counts[friction] = (
            friction_counts.get(friction, 0) + 1
        )

    expected_distribution = {
        "Positive": 8,
        "Neutral": 4,
        "Confusion": 6,
        "Difficulty": 5,
        "Clarification": 2
    }

    if friction_counts != expected_distribution:
        raise ValueError(
            f"{lecture_id}: invalid distribution: "
            f"{friction_counts}"
        )

    # ----------------------------------------
    # Source metadata
    # ----------------------------------------

    chunk_metadata = (
        lecture_df[
            [
                "chunk_id",
                "start_time",
                "end_time"
            ]
        ]
        .drop_duplicates("chunk_id")
        .set_index("chunk_id")
    )

    valid_chunk_ids = set(
        chunk_metadata.index
    )

    # ----------------------------------------
    # Validate + rebuild timestamps
    # ----------------------------------------

    for review in reviews:

        required_fields = [
            "review_id",
            "lecture_id",
            "chunk_ids",
            "timestamps",
            "review_text",
            "sentiment",
            "recurring_theme",
            "concept_tags",
            "friction_type",
            "severity",
            "source"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in review
        ]

        if missing_fields:
            raise ValueError(
                f"{lecture_id} / "
                f"{review.get('review_id')}: "
                f"missing {missing_fields}"
            )

        if review["lecture_id"] != lecture_id:
            raise ValueError(
                f"{lecture_id}: incorrect lecture_id "
                f"in {review['review_id']}"
            )

        if not review["chunk_ids"]:
            raise ValueError(
                f"{lecture_id}: empty chunk_ids in "
                f"{review['review_id']}"
            )

        # Check chunk IDs
        for chunk_id in review["chunk_ids"]:

            if chunk_id not in valid_chunk_ids:
                raise ValueError(
                    f"{lecture_id}: invalid chunk_id "
                    f"{chunk_id}"
                )

        # ------------------------------------
        # IMPORTANT:
        # Ignore Gemini timestamps.
        # Rebuild from source.
        # ------------------------------------

        review["timestamps"] = [
            {
                "start_time": chunk_metadata.loc[
                    chunk_id,
                    "start_time"
                ],
                "end_time": chunk_metadata.loc[
                    chunk_id,
                    "end_time"
                ]
            }
            for chunk_id in review["chunk_ids"]
        ]

    # ----------------------------------------
    # Save immediately
    # ----------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    production_data = {
        "lecture_id": lecture_id,
        "review_count": len(reviews),
        "reviews": reviews
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            production_data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\n{lecture_id}: "
        f"{len(reviews)} reviews generated."
    )

    print(
        f"Saved: {output_file}"
    )

    return production_data


# --------------------------------------------
# Production loop
# --------------------------------------------

successful_lectures = []
failed_lectures = []

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    output_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    # ----------------------------------------
    # Resume support
    # ----------------------------------------

    if output_file.exists():

        print(
            f"\n{lecture_id}: "
            f"already exists — SKIPPING"
        )

        successful_lectures.append(
            lecture_id
        )

        continue

    try:

        process_lecture_discussions(
            lecture_id=lecture_id,
            lecture_source=lecture_sources[
                lecture_id
            ],
            lecture_df=all_lecture_chunks[
                lecture_id
            ],
            output_file=output_file
        )

        successful_lectures.append(
            lecture_id
        )

    except Exception as e:

        failed_lectures.append({
            "lecture_id": lecture_id,
            "error": f"{type(e).__name__}: {e}"
        })

        print(
            f"\n{lecture_id}: FAILED"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        # Continue with next lecture
        continue


# --------------------------------------------
# Final summary
# --------------------------------------------

print("\n" + "=" * 60)
print("DISCUSSION GENERATION SUMMARY")
print("=" * 60)

print(
    "Successful lectures:",
    len(successful_lectures)
)

print(
    "Failed lectures:",
    len(failed_lectures)
)

if failed_lectures:

    print("\nFailed lectures:")

    for failure in failed_lectures:
        print(
            f"- {failure['lecture_id']}: "
            f"{failure['error']}"
        )

else:

    print(
        "\nSUCCESS — ALL 24 LECTURES COMPLETED"
    )


# ============================================
# STEP 11 — RETRY FAILED LECTURES
# ============================================

FAILED_LECTURES = []


def process_failed_lecture(lecture_id):

    print("\n" + "=" * 60)
    print(f"RETRYING {lecture_id}")
    print("=" * 60)

    lecture_df = all_lecture_chunks[lecture_id]

    output_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    # ----------------------------------------
    # Retry up to 3 times
    # ----------------------------------------

    for attempt in range(1, 4):

        print(
            f"\nAttempt {attempt}/3"
        )

        try:

            # Generate 25 discussions
            result = generate_lecture_discussions(
                lecture_id=lecture_id,
                lecture_source=lecture_sources[
                    lecture_id
                ],
                num_reviews=25
            )

            reviews = result.get(
                "reviews",
                []
            )

            # --------------------------------
            # Count
            # --------------------------------

            if len(reviews) != 25:
                raise ValueError(
                    f"Expected 25 reviews, "
                    f"got {len(reviews)}"
                )

            # --------------------------------
            # Normalize friction labels
            # --------------------------------

            label_map = {
                "Conceptual Confusion": "Confusion",
                "Implementation Difficulty": "Difficulty",
                "Comprehension Difficulty": "Difficulty",
                "Mathematical Difficulty": "Difficulty",
                "Clarification Needed": "Clarification",
                "Conceptual Clarification": "Clarification",
                "None": "Neutral"
            }

            for review in reviews:

                friction = review[
                    "friction_type"
                ]

                review[
                    "friction_type"
                ] = label_map.get(
                    friction,
                    friction
                )

            # --------------------------------
            # Distribution
            # --------------------------------

            friction_counts = {}

            for review in reviews:

                friction = review[
                    "friction_type"
                ]

                friction_counts[friction] = (
                    friction_counts.get(
                        friction,
                        0
                    ) + 1
                )

            expected_distribution = {
                "Positive": 8,
                "Neutral": 4,
                "Confusion": 6,
                "Difficulty": 5,
                "Clarification": 2
            }

            if (
                friction_counts
                != expected_distribution
            ):
                raise ValueError(
                    f"Invalid distribution: "
                    f"{friction_counts}"
                )

            # --------------------------------
            # Source chunk metadata
            # --------------------------------

            chunk_metadata = (
                lecture_df[
                    [
                        "chunk_id",
                        "start_time",
                        "end_time"
                    ]
                ]
                .drop_duplicates(
                    "chunk_id"
                )
                .set_index("chunk_id")
            )

            valid_chunk_ids = set(
                chunk_metadata.index
            )

            # --------------------------------
            # Validate + rebuild metadata
            # --------------------------------

            for review in reviews:

                if review[
                    "lecture_id"
                ] != lecture_id:

                    raise ValueError(
                        "Incorrect lecture_id"
                    )

                if not review[
                    "chunk_ids"
                ]:

                    raise ValueError(
                        f"{review['review_id']}: "
                        "empty chunk_ids"
                    )

                for chunk_id in review[
                    "chunk_ids"
                ]:

                    if chunk_id not in (
                        valid_chunk_ids
                    ):

                        raise ValueError(
                            f"Invalid chunk_id "
                            f"{chunk_id}"
                        )

                # --------------------------------
                # Source is authoritative
                # --------------------------------

                review[
                    "timestamps"
                ] = [

                    {
                        "start_time":
                            chunk_metadata.loc[
                                chunk_id,
                                "start_time"
                            ],

                        "end_time":
                            chunk_metadata.loc[
                                chunk_id,
                                "end_time"
                            ]
                    }

                    for chunk_id in review[
                        "chunk_ids"
                    ]
                ]

            # --------------------------------
            # Save
            # --------------------------------

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            production_data = {
                "lecture_id": lecture_id,
                "review_count": 25,
                "reviews": reviews
            }

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    production_data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"\nSUCCESS — {lecture_id}"
            )

            print(
                f"Saved: {output_file}"
            )

            return True

        except Exception as e:

            print(
                f"{lecture_id} attempt "
                f"{attempt} failed:"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            if attempt < 3:

                wait_time = 10 * attempt

                print(
                    f"Retrying in "
                    f"{wait_time}s..."
                )

                time.sleep(wait_time)

            else:

                print(
                    f"\nFAILED — {lecture_id}"
                )

                return False


# ============================================
# RETRY ONLY FAILED LECTURES
# ============================================

retry_successful = []
retry_failed = []

for lecture_id in FAILED_LECTURES:

    success = process_failed_lecture(
        lecture_id
    )

    if success:
        retry_successful.append(
            lecture_id
        )
    else:
        retry_failed.append(
            lecture_id
        )


# ============================================
# FINAL RETRY SUMMARY
# ============================================

print("\n" + "=" * 60)
print("RETRY SUMMARY")
print("=" * 60)

print(
    "Recovered:",
    len(retry_successful)
)

print(
    "Still failed:",
    len(retry_failed)
)

if retry_successful:

    print("\nRecovered lectures:")

    for lecture_id in retry_successful:
        print("-", lecture_id)

if retry_failed:

    print("\nStill failed:")

    for lecture_id in retry_failed:
        print("-", lecture_id)


# ============================================
# STEP 12 — FINAL DISCUSSION JSON VERIFICATION
# ============================================

print("=" * 60)
print("FINAL DISCUSSION DATABASE VERIFICATION")
print("=" * 60)

all_discussion_data = {}

required_fields = [
    "review_id",
    "lecture_id",
    "chunk_ids",
    "timestamps",
    "review_text",
    "sentiment",
    "recurring_theme",
    "concept_tags",
    "friction_type",
    "severity",
    "source"
]

expected_distribution = {
    "Positive": 8,
    "Neutral": 4,
    "Confusion": 6,
    "Difficulty": 5,
    "Clarification": 2
}


# --------------------------------------------
# Verify each lecture
# --------------------------------------------

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    json_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    # File must exist
    assert json_file.exists(), (
        f"Missing file: {json_file}"
    )

    # Load JSON
    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    reviews = data.get("reviews", [])

    # Exactly 25
    assert len(reviews) == 25, (
        f"{lecture_id}: "
        f"expected 25, got {len(reviews)}"
    )

    # Validate every review
    for review in reviews:

        # Required fields
        missing = [
            field
            for field in required_fields
            if field not in review
        ]

        assert not missing, (
            f"{lecture_id} / "
            f"{review.get('review_id')}: "
            f"missing {missing}"
        )

        # Lecture ID
        assert (
            review["lecture_id"]
            == lecture_id
        )

        # Chunk IDs
        assert isinstance(
            review["chunk_ids"],
            list
        )

        assert len(
            review["chunk_ids"]
        ) > 0

        # Timestamps
        assert len(
            review["timestamps"]
        ) == len(
            review["chunk_ids"]
        )

        # Source
        assert review["source"] == (
            "synthetic_ai"
        )

    # ----------------------------------------
    # Distribution
    # ----------------------------------------

    friction_counts = {}

    for review in reviews:

        friction = review[
            "friction_type"
        ]

        friction_counts[friction] = (
            friction_counts.get(
                friction,
                0
            ) + 1
        )

    assert (
        friction_counts
        == expected_distribution
    ), (
        f"{lecture_id}: invalid distribution "
        f"{friction_counts}"
    )

    all_discussion_data[
        lecture_id
    ] = data

    print(
        f"{lecture_id}: "
        f"25 reviews verified"
    )


# --------------------------------------------
# Total count
# --------------------------------------------

total_reviews = sum(
    len(
        data["reviews"]
    )
    for data in all_discussion_data.values()
)

print("\n" + "=" * 60)

print(
    "Lectures verified:",
    len(all_discussion_data)
)

print(
    "Total questions:",
    total_reviews
)

assert len(
    all_discussion_data
) == 24

assert total_reviews == 600


print("=" * 60)
print(
    "SUCCESS — ALL 24 DISCUSSION JSON FILES VERIFIED"
)
print(
    "TOTAL DISCUSSIONS: 600"
)
print("=" * 60)


# ============================================
# STEP 13 — CREATE MASTER DISCUSSION DATABASE
# ============================================

master_discussions = []

for lecture_id, data in all_discussion_data.items():

    for review in data["reviews"]:

        master_discussions.append(review)


# --------------------------------------------
# Final count check
# --------------------------------------------

assert len(master_discussions) == 600


# --------------------------------------------
# Master database structure
# --------------------------------------------

master_database = {
    "dataset_name": "course_discussion_database",
    "total_records": len(master_discussions),
    "total_lectures": 24,
    "records": master_discussions
}


# --------------------------------------------
# Save master database
# --------------------------------------------

MASTER_DISCUSSION_FILE = (
    DATABASE_DIR
    / "master_discussion_database.json"
)

with open(
    MASTER_DISCUSSION_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        master_database,
        f,
        indent=2,
        ensure_ascii=False
    )


print("=" * 60)
print("MASTER DISCUSSION DATABASE CREATED")
print("=" * 60)

print(
    "Total lectures:",
    master_database["total_lectures"]
)

print(
    "Total records:",
    master_database["total_records"]
)

print(
    "Saved:",
    MASTER_DISCUSSION_FILE
)

print("=" * 60)
print(
    "SUCCESS — MASTER DISCUSSION DATABASE SAVED"
)
print("=" * 60)


# ============================================
# STEP 14 — VERIFY MASTER DATABASE
# ============================================

with open(
    MASTER_DISCUSSION_FILE,
    "r",
    encoding="utf-8"
) as f:

    master_check = json.load(f)


records = master_check["records"]

print("=" * 60)
print("VERIFYING MASTER DISCUSSION DATABASE")
print("=" * 60)

print(
    "Total records:",
    len(records)
)

print(
    "Total lectures:",
    master_check["total_lectures"]
)


# --------------------------------------------
# Basic checks
# --------------------------------------------

assert len(records) == 600
assert master_check["total_lectures"] == 24


# --------------------------------------------
# Unique review IDs
# --------------------------------------------

review_ids = [
    record["review_id"]
    for record in records
]

assert len(review_ids) == len(
    set(review_ids)
)

print(
    "Unique review IDs: 600"
)


# --------------------------------------------
# Lecture distribution
# --------------------------------------------

lecture_counts = {}

for record in records:

    lecture_id = record["lecture_id"]

    lecture_counts[lecture_id] = (
        lecture_counts.get(
            lecture_id,
            0
        ) + 1
    )

print("\nRecords per lecture:")

for lecture_id in sorted(
    lecture_counts
):

    print(
        f"{lecture_id}: "
        f"{lecture_counts[lecture_id]}"
    )

assert len(lecture_counts) == 24

assert all(
    count == 25
    for count in lecture_counts.values()
)


# --------------------------------------------
# Final verification
# --------------------------------------------

print("\n" + "=" * 60)
print(
    "SUCCESS — MASTER DATABASE VERIFIED"
)
print("=" * 60)

print(
    "24 lectures × 25 discussions = 600"
)


# # INDIVIDUAL REVIEW JSON — STANDARDIZATION & VALIDATION

# STEP 1 — INSPECT INDIVIDUAL REVIEW JSON

review_file = (
    DISCUSSION_DIR
    / "lec01"
    / "lec01_discussion.json"
)

with open(review_file, "r", encoding="utf-8") as f:
    lec01_data = json.load(f)

print("Total reviews:", len(lec01_data["reviews"]))

print("\nFirst review:")
print(json.dumps(
    lec01_data["reviews"][0],
    indent=2,
    ensure_ascii=False
))

# STEP 2 — AUDIT ALL INDIVIDUAL REVIEW JSON FILES

required_source_fields = [
    "review_id",
    "lecture_id",
    "chunk_ids",
    "timestamps",
    "post_text",
    "sentiment",
    "recurring_theme",
    "concept_tags",
    "friction_type",
    "severity",
    "source"
]

all_review_ids = []
problems = []

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    review_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    with open(review_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    reviews = data.get("reviews", [])

    # Count
    if len(reviews) != 25:
        problems.append(
            f"{lecture_id}: expected 25 reviews, got {len(reviews)}"
        )

    for review in reviews:

        # Required fields
        missing = [
            field
            for field in required_source_fields
            if field not in review
        ]

        if missing:
            problems.append(
                f"{lecture_id} / {review.get('review_id')}: "
                f"missing {missing}"
            )

        # Blank values
        for field in required_source_fields:
            value = review.get(field)

            if value is None or value == "" or value == []:
                problems.append(
                    f"{lecture_id} / {review.get('review_id')}: "
                    f"blank {field}"
                )

        all_review_ids.append(review.get("review_id"))

print("Total reviews:", len(all_review_ids))
print("Unique review IDs:", len(set(all_review_ids)))
print("Problems:", len(problems))

if problems:
    print("\nPROBLEMS FOUND:")
    for problem in problems:
        print("-", problem)
else:
    print("\nSUCCESS — ALL 24 INDIVIDUAL JSON FILES ARE CLEAN")


# STEP 3 — BUILD STANDARDIZED lec01 REVIEW RECORDS

lecture_id = "lec01"
module_num = int(lecture_id.replace("lec", ""))

standardized_reviews = []

for i, review in enumerate(lec01_data["reviews"], start=1):

    standardized_review = {
        # Database schema
        "record_id": f"{lecture_id}_review_{i:03d}",
        "course_id": "deeplearning",
        "module_id": f"MOD_{module_num:02d}",
        "lecture_id": lecture_id,
        "discussion_id": f"discussion_{lecture_id}_{i:03d}",

        "thread_title": review["recurring_theme"],
        "post_text": review["post_text"],

        # No source value exists for these fields,
        # so we do NOT create blank fields.
        "topic": review["concept_tags"],
        "source_file": f"{lecture_id}_discussion.json",

        # Preserve original analytical metadata
        "sentiment": review["sentiment"],
        "recurring_theme": review["recurring_theme"],
        "concept_tags": review["concept_tags"],
        "friction_type": review["friction_type"],
        "severity": review["severity"],
        "chunk_ids": review["chunk_ids"],
        "timestamps": review["timestamps"],
        "source": review["source"],
    }

    standardized_reviews.append(standardized_review)

print(json.dumps(
    standardized_reviews[0],
    indent=2,
    ensure_ascii=False
))

# STEP 4 — STANDARDIZE ALL 24 INDIVIDUAL REVIEW JSON FILES

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"
    module_id = f"MOD_{lecture_num:02d}"

    review_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    with open(review_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    standardized_reviews = []

    for i, review in enumerate(data["reviews"], start=1):

        standardized_review = {
            "record_id": f"{lecture_id}_review_{i:03d}",
            "course_id": "deeplearning",
            "module_id": module_id,
            "lecture_id": lecture_id,
            "discussion_id": f"discussion_{lecture_id}_{i:03d}",

            "thread_title": review["recurring_theme"],
            "post_text": review["post_text"],
            "topic": review["concept_tags"],
            "source_file": f"{lecture_id}_discussion.json",

            # Preserve original metadata
            "sentiment": review["sentiment"],
            "recurring_theme": review["recurring_theme"],
            "concept_tags": review["concept_tags"],
            "friction_type": review["friction_type"],
            "severity": review["severity"],
            "chunk_ids": review["chunk_ids"],
            "timestamps": review["timestamps"],
            "source": review["source"]
        }

        standardized_reviews.append(standardized_review)

    data["reviews"] = standardized_reviews

    with open(review_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"{lecture_id} updated — "
        f"{len(standardized_reviews)} reviews"
    )

print("\nSUCCESS — ALL 24 INDIVIDUAL REVIEW JSON FILES UPDATED")


# STEP 5 — VERIFY STANDARDIZED REVIEW JSONs

required_fields = [
    "record_id",
    "course_id",
    "module_id",
    "lecture_id",
    "discussion_id",
    "thread_title",
    "post_text",
    "topic",
    "source_file"
]

all_record_ids = []
all_discussion_ids = []
problems = []

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"
    module_id = f"MOD_{lecture_num:02d}"

    review_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    with open(review_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    reviews = data["reviews"]

    for i, review in enumerate(reviews, start=1):

        # Required fields
        for field in required_fields:
            value = review.get(field)

            if value is None or value == "" or value == []:
                problems.append(
                    f"{lecture_id} question {i}: blank {field}"
                )

        # ID convention
        if review["record_id"] != f"{lecture_id}_review_{i:03d}":
            problems.append(f"{lecture_id} question {i}: bad record_id")

        if review["course_id"] != "deeplearning":
            problems.append(f"{lecture_id} question {i}: bad course_id")

        if review["module_id"] != module_id:
            problems.append(f"{lecture_id} question {i}: bad module_id")

        if review["lecture_id"] != lecture_id:
            problems.append(f"{lecture_id} question {i}: bad lecture_id")

        all_record_ids.append(review["record_id"])
        all_discussion_ids.append(review["discussion_id"])

    print(f"{lecture_id} → OK ({len(reviews)} reviews)")

print("\n" + "=" * 50)
print("Total records:", len(all_record_ids))
print("Unique record IDs:", len(set(all_record_ids)))
print("Unique discussion IDs:", len(set(all_discussion_ids)))
print("Problems:", len(problems))

if problems:
    print("\nPROBLEMS:")
    for p in problems:
        print("-", p)
else:
    print("\nSUCCESS — ALL 24 REVIEW FILES ARE VALID")


# STEP 6 — PRESERVE ORIGINAL review_id

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    review_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    with open(review_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, review in enumerate(data["reviews"], start=1):
        review["review_id"] = f"REV_{lecture_id}_{i:03d}"

    with open(review_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

print("review_id preserved in all 24 files.")

# STEP 7 — VERIFY review_id

all_review_ids = []
problems = []

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    review_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    with open(review_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, review in enumerate(data["reviews"], start=1):

        expected_id = f"REV_{lecture_id}_{i:03d}"

        if review.get("review_id") != expected_id:
            problems.append(
                f"{lecture_id} question {i}: "
                f"expected {expected_id}, got {review.get('review_id')}"
            )

        all_review_ids.append(review.get("review_id"))

print("Total review IDs:", len(all_review_ids))
print("Unique review IDs:", len(set(all_review_ids)))
print("Problems:", len(problems))

if problems:
    for p in problems:
        print("-", p)
else:
    print("\nSUCCESS — review_id is valid and unique.")


# # ============================================================
# # REVIEW DATABASE — MASTER BUILD, VALIDATION & EXPORT
# # ============================================================


# STEP 8 — BUILD MASTER REVIEW DATABASE

all_reviews = []

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    review_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    with open(review_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_reviews.extend(data["reviews"])


# Create DataFrame
master_review_df = pd.DataFrame(all_reviews)

print("Total records:", len(master_review_df))
print("Columns:", master_review_df.columns.tolist())


# Database folder
REVIEW_DB_DIR = DISCUSSION_DIR / "database"
REVIEW_DB_DIR.mkdir(parents=True, exist_ok=True)


# Save JSON
master_json_file = REVIEW_DB_DIR / "master_discussion_database.json"

with open(master_json_file, "w", encoding="utf-8") as f:
    json.dump(
        {
            "total_records": len(all_reviews),
            "reviews": all_reviews
        },
        f,
        indent=2,
        ensure_ascii=False
    )


# Prepare CSV
master_csv_df = master_review_df.copy()

# Convert lists/dicts to JSON strings for CSV
for col in master_csv_df.columns:
    master_csv_df[col] = master_csv_df[col].apply(
        lambda x: json.dumps(x, ensure_ascii=False)
        if isinstance(x, (list, dict))
        else x
    )


# Save CSV
master_csv_file = REVIEW_DB_DIR / "master_discussion_database.csv"

master_csv_df.to_csv(
    master_csv_file,
    index=False,
    encoding="utf-8"
)

print("\nMaster JSON:", master_json_file)
print("Master CSV:", master_csv_file)
print("\nMASTER DATABASE CREATED")


# STEP 9 — FINAL MASTER DATABASE VALIDATION

required_fields = [
    "record_id",
    "review_id",
    "course_id",
    "module_id",
    "lecture_id",
    "discussion_id",
    "thread_title",
    "post_text",
    "topic",
    "source_file"
]

# -----------------------------
# JSON validation
# -----------------------------

with open(master_json_file, "r", encoding="utf-8") as f:
    master_data = json.load(f)

records = master_data["reviews"]

print("Total records:", len(records))

# Uniqueness
record_ids = [r["record_id"] for r in records]
review_ids = [r["review_id"] for r in records]
discussion_ids = [r["discussion_id"] for r in records]

print("Unique record IDs:", len(set(record_ids)))
print("Unique review IDs:", len(set(review_ids)))
print("Unique discussion IDs:", len(set(discussion_ids)))

# Blank check
blank_fields = []

for i, record in enumerate(records, start=1):

    for field in required_fields:

        value = record.get(field)

        if value is None or value == "" or value == []:
            blank_fields.append(
                f"record {i}: {field}"
            )

print("Blank required fields:", len(blank_fields))

# Lecture check
lectures = sorted(
    set(r["lecture_id"] for r in records)
)

print("Unique lectures:", len(lectures))


# -----------------------------
# CSV validation
# -----------------------------

csv_check = pd.read_csv(master_csv_file)

print("\nCSV records:", len(csv_check))
print("CSV columns:", len(csv_check.columns))

print("\n" + "=" * 50)

if (
    len(records) == 600
    and len(set(record_ids)) == 600
    and len(set(review_ids)) == 600
    and len(set(discussion_ids)) == 600
    and len(blank_fields) == 0
    and len(lectures) == 24
    and len(csv_check) == 600
):
    print("SUCCESS — MASTER REVIEW DATABASE VALIDATED")
else:
    print("CHECK FAILED — REVIEW THE VALUES ABOVE")


# STEP 10 — INDIVIDUAL vs MASTER CONSISTENCY

individual_record_ids = set()

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    review_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    with open(review_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for review in data["reviews"]:
        individual_record_ids.add(review["record_id"])


# Master IDs
master_record_ids = set(
    record["record_id"]
    for record in records
)

print("Individual records:", len(individual_record_ids))
print("Master records:", len(master_record_ids))

print(
    "Missing from master:",
    len(individual_record_ids - master_record_ids)
)

print(
    "Missing from individual files:",
    len(master_record_ids - individual_record_ids)
)

if (
    individual_record_ids == master_record_ids
    and len(individual_record_ids) == 600
):
    print("\nSUCCESS — INDIVIDUAL AND MASTER DATABASES MATCH")
else:
    print("\nCHECK FAILED")


# STEP 11 — CREATE CSV BACKUPS FOR ALL INDIVIDUAL REVIEW JSONs

for lecture_num in range(1, 25):

    lecture_id = f"lec{lecture_num:02d}"

    json_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.json"
    )

    csv_file = (
        DISCUSSION_DIR
        / lecture_id
        / f"{lecture_id}_discussion.csv"
    )

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data["reviews"])

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

    print(f"{lecture_id} → CSV backup created ({len(df)} records)")

print("\nSUCCESS — ALL 24 INDIVIDUAL CSV BACKUPS CREATED")



