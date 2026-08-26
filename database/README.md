# COURSEERA ALMAX Multimodal Database Pipeline

## 1. Project Overview

The COURSEERA ALMAX database pipeline prepares multimodal educational content for semantic retrieval and Retrieval-Augmented Generation (RAG).

The platform combines information from five content types:

1. Caption chunks representing the instructor’s spoken explanation
2. Lecture slides containing textual and visual instructional content
3. Caption-linked video frames showing what appeared during an explanation
4. Quiz questions connected to their supporting lecture content
5. Discussion records representing learner feedback, confusion and recurring themes

Each record is converted into a 768-dimensional embedding and stored with its metadata in one centralised Qdrant collection.

The centralised design allows the backend to retrieve related captions, slides, frames, quizzes and discussions through a single semantic-search interface.

---

## 2. Pipeline Objectives

The database pipeline is designed to:

- Discover and organise course assets
- Validate videos, captions, transcripts and slide files
- Convert unstructured content into structured database records
- Preserve lecture, timestamp, slide and source references
- Analyse slide and frame images using a multimodal model
- Connect caption-linked frames with spoken explanations
- Connect quizzes and discussions with supporting caption chunks
- Generate consistent text embeddings across all content types
- Upload vectors and metadata into one Qdrant collection
- Store database-referenced slides and caption-linked frames in a private Hugging Face dataset
- Add portable visual-asset references to the existing Qdrant slide and frame payloads
- Validate record counts, identifiers, payloads and relationships
- Provide searchable textual and visual evidence for backend and RAG applications

---

## 3. High-Level Data Flow

```text
Raw course assets
        │
        ├── Videos
        ├── WebVTT captions
        ├── Transcript PDFs
        ├── Slide PDFs
        ├── Quiz data
        └── Discussion data
        │
        ▼
Discovery and validation
        │
        ▼
Content extraction and preprocessing
        │
        ├── Caption chunking
        ├── Transcript extraction
        ├── Slide-image extraction
        └── Caption-linked frame extraction
        │
        ▼
Gemini visual analysis
        │
        ├── Slide analysis
        └── Frame analysis
        │
        ▼
Structured databases
        │
        ├── Caption database
        ├── Slide database
        ├── Frame database
        ├── Quiz database
        └── Discussion database
        │
        ▼
BGE embedding generation
        │
        ▼
Centralised Qdrant collection
        │
        ▼
Private Hugging Face visual dataset
        │
        ├── Slide images
        └── Caption-linked frames
        │
        ▼
Backend retrieval and RAG
```

---

## 4. Repository Structure

```text
database/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── discovery.py
│   ├── extraction.py
│   ├── frame_audit.py
│   ├── visual_analysis.py
│   ├── visual_database.py
│   ├── caption_databases.py
│   ├── quiz_db.py
│   ├── discussion_db.py
│   ├── embeddings.py
│   ├── quiz_discussion_embedding.py
│   ├── qdrant_db.py
│   ├── quiz_discussion_qdrant.py
│   ├── validation.py
│   ├── visual_asset_qdrant.py
│   └── pipeline.py
│
├── requirements.txt
└── README.md
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Defines project paths and shared configuration |
| `discovery.py` | Discovers source assets and creates the inventory |
| `extraction.py` | Extracts and preprocesses course content |
| `frame_audit.py` | Extracts representative caption-linked video frames |
| `visual_analysis.py` | Analyses slides and frames using Gemini |
| `visual_database.py` | Creates structured slide and frame records |
| `caption_databases.py` | Creates the caption database |
| `quiz_db.py` | Creates or prepares quiz records |
| `discussion_db.py` | Creates or prepares discussion records |
| `embeddings.py` | Generates caption, slide and frame embeddings |
| `quiz_discussion_embedding.py` | Generates quiz and discussion embeddings |
| `qdrant_db.py` | Uploads caption, slide and frame points |
| `quiz_discussion_qdrant.py` | Integrates quiz and discussion points |
| `visual_asset_qdrant.py` | Adds Hugging Face visual-asset references to existing slide and frame payloads |
| `validation.py` | Validates databases, embeddings and outputs |
| `pipeline.py` | Coordinates major pipeline stages |

The repository contains pipeline code only. Raw files and generated outputs are stored locally or in approved shared storage.

---

## 5. Local Data Structure

The complete local project may use the following structure:

```text
COURSEERA_ALMAX/
├── raw/
│   ├── videos/
│   ├── captions/
│   ├── transcripts/
│   ├── slides/
│   ├── quizzes/
│   └── discussions/
│
├── processed/
│   ├── inventories/
│   ├── transcripts/
│   ├── slide_images/
│   ├── frame_audit/
│   ├── visual_analysis/
│   ├── databases/
│   └── embeddings/
│
├── src/
├── .env
└── requirements.txt
```

Folder names may differ according to the paths defined in `src/config.py`.

---

## 6. Prerequisites

Recommended environment:

```text
Python: 3.10 or later
Operating system: Windows, Linux or macOS
Vector database: Qdrant Cloud or local Qdrant
Embedding model: BAAI/bge-base-en-v1.5
```

The computer should have enough storage for lecture videos, PDFs, extracted slide images, frames and embedding files.

---

## 7. Installation

### 7.1 Clone the Repository

```powershell
git clone <repository-url>
cd coursera-mip
```

### 7.2 Create a Virtual Environment

From the repository root:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

### 7.3 Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r database\requirements.txt
```

Check the installed packages:

```powershell
pip check
```

---

## 8. Environment Variables

Create a local `.env` file containing the required credentials.

```env
QDRANT_URL=
QDRANT_API_KEY=
GEMINI_API_KEY=
HF_TOKEN=
```

Verify the exact Gemini variable name used in `visual_analysis.py`. If the code uses another name, use that name in `.env`.

### Environment-Variable Purpose

| Variable | Purpose |
|---|---|
| `QDRANT_URL` | Qdrant Cloud cluster endpoint |
| `QDRANT_API_KEY` | Authorised key for accessing Qdrant |
| `GEMINI_API_KEY` | Key used for slide and frame visual analysis |
| `HF_TOKEN` | Private Hugging Face dataset access token used by the backend for visual retrieval |

`HF_TOKEN` is not required by `visual_asset_qdrant.py`; it is required by the backend when retrieving files from the private visual dataset. Never commit `.env` or paste API keys into documentation, screenshots, chat messages or source code.

---

## 9. Required Input Files

| Content | Format | Purpose |
|---|---|---|
| Lecture video | `.mp4` | Video metadata and frame extraction |
| Captions | `.vtt` | Timestamped instructor speech |
| Transcript | `.pdf` | Transcript validation and extraction |
| Lecture slides | `.pdf` | Slide-image extraction and visual analysis |
| Quiz records | `.csv` or source JSON | Assessment database |
| Discussion records | `.csv` or source JSON | Learner-discussion database |

The source assets must use consistent lecture identifiers, such as:

```text
lec01
lec02
lec03
```

Lecture 22 was unavailable in the current source course package and was therefore excluded from the validated quiz and discussion integration.

---

## 10. Source Discovery and Validation

The discovery stage:

- Scans source directories
- Identifies available lecture assets
- Maps videos, captions, transcripts and slides to lectures
- Detects missing or unmatched files
- Records file locations and processing status
- Produces a structured asset inventory

Validation should occur before expensive extraction or model calls.

Important checks include:

- File existence
- Correct file extension
- Valid lecture mapping
- Video readability
- Caption readability
- PDF readability
- Missing source assets
- Duplicate identifiers

---

## 11. Caption Processing

WebVTT caption files contain timestamped spoken text.

Caption processing:

1. Parses individual WebVTT caption segments
2. Preserves starting and ending timestamps
3. Groups related segments into meaningful chunks
4. Calculates chunk duration and word count
5. Assigns a unique `chunk_id`
6. Stores the processed content in the caption database

Example chunk identifier:

```text
lec01_caption_chunk_01
```

The caption database represents what the instructor said during each lecture interval.

---

## 12. Slide Processing

Slide PDFs are converted into individual images using PyMuPDF.

Each slide record retains:

- Lecture identifier
- Slide number
- Image filename
- Image path
- Image width
- Image height
- Image size
- Extraction status

The images are subsequently analysed using Gemini to extract:

- Summary
- Visible text
- Visual type
- Diagram explanation
- Graph explanation
- Equations
- Key concepts
- Visual–text relationship
- Content category
- Human-review flag
- Instructional-evidence flag

---

## 13. Caption-Linked Frame Extraction

Simple fixed-interval frame extraction was not used because lecture videos mainly displayed and explained presentation slides.

Fixed-time extraction could capture:

- Repeated slides
- Slide transitions
- Blank frames
- Animations in progress
- Frames unrelated to the spoken explanation

Instead, one representative frame was selected using the midpoint of each caption chunk:

```text
Frame timestamp =
(Caption start time + Caption end time) / 2
```

This creates a direct relationship between:

```text
Caption text → What the instructor said
Frame image  → What the instructor displayed
```

Frame records use `primary_chunk_id` to retain this relationship.

---

## 14. Visual Analysis

Gemini analyses both:

- Extracted slide images
- Caption-linked video frames

The same structured analysis schema is used for both visual sources. The `source_type` field distinguishes them:

```text
source_type = slide
source_type = frame
```

The structured visual descriptions are later converted into text embeddings.

Images themselves are not directly embedded by the BGE model.

```text
Slide image
→ Gemini textual analysis
→ BGE embedding

Video frame
→ Gemini textual analysis
→ BGE embedding
```

---

## 15. Structured Databases

The pipeline creates five structured databases.

### 15.1 Caption Database

Represents timestamped spoken explanations.

Important fields include:

```text
record_id
chunk_id
course_id
module_id
lecture_id
start_time
end_time
start_seconds
end_seconds
text
word_count
duration_seconds
content_type
```

### 15.2 Slide Database

Combines slide-image metadata with Gemini visual analysis.

Important fields include:

```text
record_id
lecture_id
slide_no
image_file_name
image_file_path
summary
visual_types
visual_text
diagram_explanation
graph_explanation
equations
key_concepts
content_category
needs_human_review
is_instructional_evidence
```

### 15.3 Frame Database

Combines frame-audit metadata with Gemini analysis.

Important fields include:

```text
record_id
frame_id
lecture_id
primary_chunk_id
timestamp_seconds
frame_filename
frame_file_path
summary
visual_types
visual_text
key_concepts
content_category
is_instructional_evidence
```

### 15.4 Quiz Database

Represents assessment questions connected to supporting lecture content.

Important fields include:

```text
record_id
lecture_id
quiz_id
question_id
question
options
correct_answer
explanation
topic
difficulty_signals
concept_tags
assessment_location
alignment_score
question_type
```

### 15.5 Discussion Database

Represents synthetic learner feedback and discussion signals.

Important fields include:

```text
record_id
lecture_id
discussion_id
thread_title
post_text
topic
sentiment
recurring_theme
concept_tags
friction_type
severity
chunk_ids
timestamps
source
review_id
```

---

## 16. Cross-Modal Relationships

The five databases are logically connected through shared metadata:

```text
course_id
module_id
lecture_id
```

### Frame-to-Caption Relationship

```text
frame.primary_chunk_id
=
caption.chunk_id
```

This connects a displayed frame with the instructor’s spoken explanation.

### Quiz-to-Caption Relationship

```text
quiz.linked_chunk_ids
→ caption.chunk_id
```

This connects an assessment question with the lecture content supporting it.

### Discussion-to-Caption Relationship

```text
discussion.linked_chunk_ids
→ caption.chunk_id
```

This connects learner feedback or confusion with the relevant lecture explanation.

Qdrant does not enforce these links as relational foreign keys. The backend uses payload metadata to retrieve and combine related records.

---

## 17. Data Integration Validation

Before embedding generation, validation checks include:

- Unique `record_id` values
- No duplicate records
- Required identifiers present
- Valid lecture identifiers
- Valid caption-chunk references
- Correct quiz answer present in the options
- Matching discussion chunk and timestamp list lengths
- Searchable content present
- Valid content-type labels
- Expected record counts

### Quiz and Discussion Cleaning

The received quiz and discussion files originally included Lecture 22 records. These were excluded because the corresponding course source assets were unavailable.

Caption references were also standardised from three-digit formatting:

```text
lec01_caption_chunk_001
```

to the caption-database format:

```text
lec01_caption_chunk_01
```

Records containing only nonexistent caption references were excluded. One discussion record containing both valid and invalid references was retained after removing only the invalid reference.

---

## 18. Embedding Generation

All five content types use:

```text
Model: BAAI/bge-base-en-v1.5
Dimensions: 768
Normalization: L2
Distance metric: Cosine
```

### Text Used for Embedding

| Content type | Searchable representation |
|---|---|
| Caption | Caption-chunk text |
| Slide | Visual summary, visible text, explanations, equations and concepts |
| Frame | Visual summary, visible text, explanations, equations and concepts |
| Quiz | Question, options, answer, explanation, topic and concepts |
| Discussion | Title, post, topic, themes, concepts, sentiment and severity |

Administrative fields such as local file paths and image sizes are stored as payload metadata but are not used as semantic embedding input.

---

## 19. Embedding Commands

Run from inside `database`.

### Compile Modules

```powershell
python -m compileall src
```

### Generate Caption, Slide and Frame Embeddings

```powershell
python -m src.embeddings
```

### Generate Quiz and Discussion Embeddings

```powershell
python -m src.quiz_discussion_embedding
```

Generated files:

```text
processed/embeddings/
├── caption_database_embeddings.json
├── slide_database_embeddings.json
├── frame_database_embeddings.json
├── quiz_database_embeddings.json
└── discussion_database_embeddings.json
```

---

## 20. Embedding Validation

| Validation check | Caption | Slide | Frame | Quiz | Discussion |
|---|---:|---:|---:|---:|---:|
| Database records | 1,572 | 1,420 | 1,267 | 456 | 570 |
| Embeddings | 1,572 | 1,420 | 1,267 | 456 | 570 |
| Dimensions | 768 | 768 | 768 | 768 | 768 |
| Invalid dimensions | 0 | 0 | 0 | 0 | 0 |
| Duplicate IDs | 0 | 0 | 0 | 0 | 0 |
| Vector norm | ≈1.0 | ≈1.0 | ≈1.0 | ≈1.0 | ≈1.0 |

All database records have a one-to-one matching embedding.

---

## 21. Qdrant Configuration

```text
Collection name: COURSEERA_ALMAX_MULTIMODAL
Vector dimensions: 768
Distance metric: Cosine
Payload index: content_type (keyword)
```

Supported content-type values:

```text
caption
slide
frame
quiz
discussion
```

The `content_type` keyword index supports filtered counts and retrieval.

---

## 22. Qdrant Upload

### Upload Initial Modalities

```powershell
python -m src.qdrant_db
```

This uploads:

- Caption records
- Slide records
- Frame records

### Integrate Quiz and Discussion

```powershell
python -m src.quiz_discussion_qdrant
```

The integration script:

- Discovers existing Qdrant counts dynamically
- Validates local database counts
- Checks embedding compatibility
- Builds complete payloads
- Adds `linked_chunk_ids`
- Uploads in batches
- Uses deterministic UUID5 point identifiers
- Supports safe reruns
- Validates final content-type counts

Deterministic point identifiers prevent duplicate points during reruns.

### Integrate Visual-Asset References

The database-referenced slide images and caption-linked frames are stored in the private Hugging Face dataset:

```text
pranaybannu/COURSEERA_ALMAX_VISUALS
```

Run the visual-payload integration after the slide and frame points already exist in Qdrant:

```powershell
python -m py_compile src\visual_asset_qdrant.py
python -m src.visual_asset_qdrant
```

The script:

- Loads the final slide and frame databases
- Builds portable repository-relative asset paths
- Matches records to existing Qdrant points using deterministic UUID5 identifiers
- Adds only the visual-asset payload fields
- Preserves existing vectors and payload metadata
- Validates every updated visual point
- Confirms dynamically that the collection count remains unchanged

The operation is idempotent and can be safely rerun for the same records.

---

## 23. Final Qdrant Counts

| Content type | Points |
|---|---:|
| Caption | 1,572 |
| Slide | 1,420 |
| Frame | 1,267 |
| Quiz | 456 |
| Discussion | 570 |
| **Total** | **5,285** |

Final validation confirmed:

- 5,285 total points
- Correct content-type distribution
- 768-dimensional vectors
- Consistent embedding model
- Populated payload metadata
- Valid frame-to-caption references
- Valid quiz-to-caption references
- Valid discussion-to-caption references

```text
Visual payloads updated: 2687/2687
Qdrant visual records validated: 2687/2687
Invalid Qdrant visual records: 0
Point count before: 5285
Point count after: 5285
```

The unchanged point count confirms that existing slide and frame points were enriched rather than duplicated.

---

## 24. Backend and RAG Instructions

The backend and RAG teams should:

1. Connect using the Qdrant cluster URL.
2. Use a restricted backend API key.
3. Use the collection:

```text
COURSEERA_ALMAX_MULTIMODAL
```

4. Generate query embeddings using:

```text
BAAI/bge-base-en-v1.5
```

5. Normalize query embeddings.
6. Use 768-dimensional vectors.
7. Apply filters when necessary:

```text
content_type
course_id
module_id
lecture_id
```

8. Retrieve relevant payload metadata with each result.
9. Use `primary_chunk_id` for frame-caption relationships.
10. Use `linked_chunk_ids` for quiz-caption and discussion-caption relationships.
11. Include source identifiers and timestamps in citations.
12. Avoid exposing local file paths to frontend users.
13. For slide and frame results, read `asset_repo_id`, `asset_repo_type`, `asset_revision`, `asset_path` and `mime_type`.
14. Configure `HF_TOKEN` only in the backend environment.
15. Retrieve the private visual file on the backend and proxy it to the frontend without exposing the token.

### Example Retrieval Logic

```text
User query
→ Generate normalized BGE query embedding
→ Search Qdrant
→ Retrieve related multimodal points
→ Group or filter by lecture and content type
→ Follow linked caption references
→ Assemble evidence
→ Send evidence to the LLM
→ Generate a cited response
```

---

## 25. Visual Evidence Storage and Retrieval

Qdrant stores vectors, searchable metadata and visual-asset references. It does not store the actual slide or frame image binaries.

The database-referenced visuals are stored in the private Hugging Face dataset:

```text
Repository: pranaybannu/COURSEERA_ALMAX_VISUALS
Repository type: dataset
Visibility: private
```

### Stored Visual Assets

| Visual type | Files |
|---|---:|
| Slide images | 1,420 |
| Caption-linked frames | 1,267 |
| **Total** | **2,687** |

Only files represented in the final slide and frame databases were uploaded. Extra extracted files that were not represented by Qdrant points were excluded.

```text
COURSEERA_ALMAX_VISUALS/
├── slides/
│   ├── lec01/
│   │   ├── lec01_slide_001.png
│   │   └── ...
│   └── ...
└── frames/
    ├── lec01/
    │   ├── frame_lec01_001.jpg
    │   └── ...
    └── ...
```

### Visual Fields Added to Qdrant

| Field | Purpose |
|---|---|
| `asset_provider` | Identifies Hugging Face as the visual storage provider |
| `asset_repo_id` | Identifies the private dataset repository |
| `asset_repo_type` | Identifies the repository as a dataset |
| `asset_revision` | Identifies the repository revision, currently `main` |
| `asset_path` | Portable path of the image inside the dataset |
| `mime_type` | Identifies the image format |

Example slide fields:

```json
{
  "asset_provider": "HuggingFace",
  "asset_repo_id": "pranaybannu/COURSEERA_ALMAX_VISUALS",
  "asset_repo_type": "dataset",
  "asset_revision": "main",
  "asset_path": "slides/lec01/lec01_slide_001.png",
  "mime_type": "image/png"
}
```

Example frame fields:

```json
{
  "asset_provider": "HuggingFace",
  "asset_repo_id": "pranaybannu/COURSEERA_ALMAX_VISUALS",
  "asset_repo_type": "dataset",
  "asset_revision": "main",
  "asset_path": "frames/lec01/frame_lec01_001.jpg",
  "mime_type": "image/jpeg"
}
```

Local fields such as `image_file_path` and `frame_file_path` are retained only for audit and reproducibility. They cannot be used by a backend running on another computer.

### Backend Visual Retrieval

The backend requires the following environment variable:

```text
HF_TOKEN
```

The token must have read permission for the private dataset. It must remain on the backend and must never be returned to the frontend, stored in Qdrant or committed to Git.

The backend can retrieve an image using:

```python
import os

from huggingface_hub import hf_hub_download


asset_file = hf_hub_download(
    repo_id=payload["asset_repo_id"],
    repo_type=payload["asset_repo_type"],
    revision=payload["asset_revision"],
    filename=payload["asset_path"],
    token=os.environ["HF_TOKEN"],
)
```

The backend should serve or proxy the downloaded file through an authenticated application endpoint. Do not store images as Base64 values inside Qdrant.

Frame evidence can additionally use `primary_chunk_id` and `timestamp_seconds` to connect the image with the instructor explanation and video location. Slide evidence can use `lecture_id` and `slide_no` to identify its original position.

---

## 26. Validation Commands

### Compile Source Code

```powershell
python -m compileall src
```

### Run Pipeline Validation

```powershell
python -m src.validation
```

### Add and Validate Visual-Asset Payloads

```powershell
python -m src.visual_asset_qdrant
```

### Check Installed Packages

```powershell
pip check
```

### Check Qdrant Point Count

```python
client.count(
    collection_name="COURSEERA_ALMAX_MULTIMODAL",
    exact=True,
)
```

Expected total:

```text
5285
```

---

## 27. Files Excluded from Git

The following should not be committed:

```gitignore
.env
__pycache__/
*.pyc

raw/
processed/
COURSEERA_ALMAX_VISUALS_UPLOAD/

*.mp4
*.avi
*.mov

*_embeddings.json
visual_retrieval_test.py
```

Also exclude:

- API keys
- Personal file paths
- Temporary outputs
- Downloaded videos
- Extracted slide images
- Extracted frames
- Large PDF files
- Database backups
- Virtual environments

---

## 28. Security Guidelines

- Never commit `.env`.
- Never commit administrative API keys.
- Share the backend Qdrant key privately.
- Use restricted access where supported.
- Do not place credentials in screenshots.
- Do not expose local directory paths.
- Rotate any credential that is accidentally exposed.
- Do not log complete secrets in terminal output.
- Keep Gemini and Qdrant credentials separate.
- Keep the Hugging Face token separate from Gemini and Qdrant credentials.
- Give the backend Hugging Face token read access only.
- Never store `HF_TOKEN` in a Qdrant payload or frontend configuration.

---

## 29. Troubleshooting

### Missing Database File

Confirm that the expected CSV exists under:

```text
processed/databases/
```

### Missing Embedding File

Generate embeddings before running the Qdrant upload.

### Wrong Vector Dimensions

All records must use 768-dimensional vectors from:

```text
BAAI/bge-base-en-v1.5
```

### Qdrant Filter Requires an Index

Create a keyword payload index for:

```text
content_type
```

### Qdrant Payload Contains Null Values

Check the payload-cleaning function and ensure supported strings, numbers, lists and dictionaries are preserved.

### Local Image Does Not Display in Qdrant

Qdrant Cloud cannot access files stored on a local computer. Confirm that the point contains `asset_repo_id` and `asset_path`, that the file exists in `pranaybannu/COURSEERA_ALMAX_VISUALS`, and that the backend has a valid `HF_TOKEN`.

### Hugging Face Returns an Authorisation Error

Confirm that:

- `HF_TOKEN` exists in the backend environment
- The token has read permission for the private dataset
- The repository ID is `pranaybannu/COURSEERA_ALMAX_VISUALS`
- The requested `asset_path` matches the path stored in Qdrant

### Qdrant Visual Count Changes

`visual_asset_qdrant.py` should only update existing payloads. If the total changes, stop the process and confirm that the script uses `set_payload` with existing deterministic point IDs rather than uploading new points.

### Repeated Upload

The upload scripts use deterministic UUID5 point IDs. Re-uploading the same `record_id` updates the existing point instead of creating a duplicate.

---

## 30. Current Project Status

Completed:

- Asset discovery and organisation
- Caption processing
- Transcript validation
- Slide-image extraction
- Caption-linked frame extraction
- Gemini slide and frame analysis
- Five structured databases
- Quiz and discussion integration
- Five embedding datasets
- Centralised Qdrant collection
- Payload and count validation
- Private Hugging Face visual dataset containing 2,687 database-referenced assets
- Portable visual-asset metadata added to all 1,420 slide and 1,267 frame points
- End-to-end Qdrant-to-private-asset access validation
- Backend Qdrant access handoff

Current validated Qdrant total:

## 31. Application Database and Analytics

Supabase PostgreSQL is used as the application database for storing user activity generated by the backend and RAG system.

It complements the existing infrastructure:

| Component | Responsibility |
|---|---|
| Qdrant | Semantic retrieval across captions, slides, frames, quizzes and discussions |
| Hugging Face | Storage and delivery of slide and caption-linked frame files |
| Supabase PostgreSQL | Conversations, queries, responses, evidence references, recommendations, feedback and analytics |
| Backend/RAG | Coordinates Qdrant retrieval, LLM generation and Supabase persistence |

The existing `COURSEERA_ALMAX_MULTIMODAL` Qdrant collection remains unchanged. Course embeddings and complete course records are not duplicated in Supabase.

### Supabase Tables

The application schema contains six related tables:

| Table | Purpose |
|---|---|
| `conversations` | Stores user or anonymous conversation sessions |
| `user_queries` | Stores submitted queries and normalized topics |
| `generated_responses` | Stores generated RAG/LLM answers and model metadata |
| `retrieval_evidence` | Stores references to Qdrant records used as evidence |
| `recommendations` | Stores recommendations generated for a response |
| `user_feedback` | Stores ratings, helpfulness and approval information |

The primary relationship is:

```text
conversations
└── user_queries
    └── generated_responses
        ├── retrieval_evidence
        ├── recommendations
        └── user_feedback
```

Deleting a query removes its associated response, evidence, recommendations and feedback through cascading foreign-key relationships.

### Qdrant Evidence References

The `retrieval_evidence` table stores references to retrieved Qdrant points rather than duplicating vectors or complete payloads.

Important fields include:

```text
qdrant_record_id
content_type
lecture_id
module_id
similarity_score
retrieval_rank
evidence_text
asset_path
timestamp_seconds
```

The `qdrant_record_id` connects a saved response to the exact caption, slide, frame, quiz or discussion record used by the RAG system.

For visual evidence, `asset_path` points to the corresponding file in:

```text
pranaybannu/COURSEERA_ALMAX_VISUALS
```

### Dashboard Analytics Views

The following PostgreSQL views support administrative dashboards:

| View | Purpose |
|---|---|
| `dashboard_popular_topics` | Shows frequently requested normalized topics |
| `dashboard_evidence_usage` | Summarizes evidence usage by content type |
| `dashboard_lecture_usage` | Identifies lectures most frequently used as evidence |
| `dashboard_feedback_summary` | Summarizes ratings, helpfulness and approval |
| `dashboard_activity_summary` | Returns overall application activity counts |

The administrative dashboard must access these views through the secured backend.

### Security

Row-Level Security is enabled on all six application tables.

Authenticated users can access only their own conversations and related records. Backend-generated queries, responses, evidence and recommendations are written using the backend-only Supabase secret key.


### Required Environment Variables

Add the following values to the backend `.env` file:

```env
SUPABASE_URL=
SUPABASE_SECRET_KEY=
```

### Python Dependency

Install the Supabase Python client:

```bash
pip install supabase
```

The dependency is also included in `requirements.txt`.

### Backend Database Helper

The reusable Supabase helper is located at:

```text
src/supabase_db.py
```

Example initialization:

```python
from src.supabase_db import SupabaseApplicationDB

application_db = SupabaseApplicationDB()
```

The backend can use it to:

```python
conversation_id = application_db.create_conversation(
    session_id="application-session-id",
    title="Course assistance",
)
```

After Qdrant retrieval and LLM generation:

```python
saved_interaction = application_db.save_rag_interaction(
    conversation_id=conversation_id,
    query_text=user_query,
    normalized_topic=normalized_topic,
    detected_intent=detected_intent,
    generated_answer=generated_answer,
    model_name=model_name,
    model_provider=model_provider,
    evidence=retrieved_evidence,
    recommendations=generated_recommendations,
)
```

Feedback can be stored separately:

```python
application_db.save_feedback(
    response_id=saved_interaction["response_id"],
    rating=5,
    is_helpful=True,
    approval="approved",
)
```

### SQL Definitions

The Supabase schema is versioned in:

```text
sql/supabase_schema.sql
sql/supabase_rls.sql
sql/supabase_dashboard_views.sql
```

These files contain database definitions only. They do not contain credentials, user records, embeddings or Qdrant data.

### Current Validation Status

The following workflow has been successfully validated:

```text
Conversation creation
→ Query storage
→ Generated-response storage
→ Qdrant evidence reference storage
→ Recommendation storage
→ User-feedback storage
→ Dashboard aggregation
```

The validation confirmed that the six tables were connected correctly and that the complete RAG interaction could be reconstructed through their foreign-key relationships.

```text
5,285 points
```

The database and visual-evidence layers are ready for backend retrieval and RAG integration.
