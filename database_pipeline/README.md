# COURSEERA ALMAX Database Pipeline

## 1. Purpose

This pipeline processes multimodal course content and prepares it for semantic retrieval and Retrieval-Augmented Generation (RAG).

It currently integrates five content types:

- Caption chunks
- Lecture slides
- Caption-linked video frames
- Quiz questions
- Discussion records

The processed records are converted into embeddings and stored in one centralised Qdrant collection.

## 2. Project Structure

```text
database_pipeline/
├── src/
│   ├── config.py
│   ├── discovery.py
│   ├── extraction.py
│   ├── frame_audit.py
│   ├── visual_analysis.py
│   ├── visual_database.py
│   ├── databases.py
│   ├── quiz_db.py
│   ├── discussion_db.py
│   ├── embeddings.py
│   ├── quiz_discussion_embedding.py
│   ├── qdrant_db.py
│   ├── quiz_discussion_qdrant.py
│   ├── validation.py
│   └── pipeline.py
├── requirements.txt
└── README.md
```

The `raw/` and `processed/` directories are maintained locally and are not committed to Git.

## 3. Installation

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r database_pipeline\requirements.txt
```

Move into the pipeline directory before running modules:

```powershell
cd database_pipeline
```

## 4. Environment Variables

Create a local `.env` file containing the required credentials:

```env
QDRANT_URL=
QDRANT_API_KEY=
GEMINI_API_KEY=
```

Do not commit `.env` or any API key to GitHub.

## 5. Required Inputs

The complete pipeline requires:

| Input | Format | Purpose |
|---|---|---|
| Lecture videos | `.mp4` | Frame extraction and video metadata |
| Captions | `.vtt` | Timestamped caption chunks |
| Transcripts | `.pdf` | Transcript validation and extraction |
| Lecture slides | `.pdf` | Slide-image extraction |
| Quiz database | `.csv` | Assessment records |
| Discussion database | `.csv` | Learner-discussion records |

Quiz and discussion records must contain valid references to the corresponding caption chunk IDs.

## 6. Database and Embedding Commands

Run commands from inside `database_pipeline`.

### Validate Python files

```powershell
python -m compileall src
```

### Run the main processing pipeline

```powershell
python -m src.pipeline
```

### Generate caption, slide and frame embeddings

```powershell
python -m src.embeddings
```

### Generate quiz and discussion embeddings

```powershell
python -m src.quiz_discussion_embedding
```

### Validate processed outputs

```powershell
python -m src.validation
```

### Upload caption, slide and frame records to Qdrant

```powershell
python -m src.qdrant_db
```

### Integrate quiz and discussion records into Qdrant

```powershell
python -m src.quiz_discussion_qdrant
```

The Qdrant scripts use deterministic UUID5 point identifiers, allowing records to be safely re-upserted without creating duplicate points.

## 7. Embedding Configuration

```text
Model: BAAI/bge-base-en-v1.5
Dimensions: 768
Normalization: L2
Distance metric: Cosine
```

The same embedding model is used for all five content types so that they can be searched within one semantic vector space.

## 8. Qdrant Configuration

```text
Collection: COURSEERA_ALMAX_MULTIMODAL
Vector dimensions: 768
Distance metric: Cosine
Payload index: content_type (keyword)
```

The following `content_type` values are used:

```text
caption
slide
frame
quiz
discussion
```

## 9. Current Validated Counts

| Content type | Records |
|---|---:|
| Caption | 1,572 |
| Slide | 1,420 |
| Frame | 1,267 |
| Quiz | 456 |
| Discussion | 570 |
| **Total** | **5,285** |

All 5,285 records have matching 768-dimensional embeddings and unique record identifiers.

## 10. Generated Outputs

The pipeline generates:

```text
processed/
├── databases/
│   ├── caption_database.csv
│   ├── slide_database.csv
│   ├── frame_database.csv
│   ├── quiz_database.csv
│   └── discussion_database.csv
└── embeddings/
    ├── caption_database_embeddings.json
    ├── slide_database_embeddings.json
    ├── frame_database_embeddings.json
    ├── quiz_database_embeddings.json
    └── discussion_database_embeddings.json
```

Generated files are excluded from Git because they are large and can be recreated from the source data.

## 11. Files Excluded from Git

The following must not be committed:

```gitignore
.env
__pycache__/
*.pyc

raw/
processed/

*.mp4
*.avi
*.mov
*_embeddings.json
```

Source videos, PDFs, extracted images, frames, databases and embeddings should be shared through approved storage or regenerated locally.

## 12. Backend and RAG Integration

Backend and RAG services should:

1. Connect using the Qdrant cluster URL and a restricted backend API key.
2. Use `COURSEERA_ALMAX_MULTIMODAL` as the collection.
3. Generate query vectors using `BAAI/bge-base-en-v1.5`.
4. Use 768-dimensional, L2-normalized query vectors.
5. Filter results using payload fields such as:
   - `content_type`
   - `course_id`
   - `module_id`
   - `lecture_id`
6. Use `primary_chunk_id` to connect frames with caption chunks.
7. Use `linked_chunk_ids` to connect quizzes and discussions with supporting caption chunks.
8. Return source identifiers and timestamps with retrieved evidence.
9. Avoid displaying local `image_file_path` values outside the source computer.

Actual images are not stored in Qdrant. If the frontend must display slides or frames, upload the images to shared object storage and store an accessible image URL in the payload.

## 13. Security

- Never commit Qdrant or Gemini API keys.
- Never share the administrative Qdrant key.
- Share the backend key privately.
- Do not expose local file paths or personal directories.
- Rotate any credential that is accidentally exposed.
