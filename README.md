# Resume Matcher System

End-to-end local Resume Parsing + Resume-to-JD Matching built with FastAPI, MongoDB, Qdrant, PaddleOCR, PyMuPDF, SentenceTransformer (local), and rule-based NLP.

## Features
- Multi-format resume ingestion: PDF (text + scanned), DOCX, PNG/JPG images
- Adaptive extraction: PyMuPDF, PaddleOCR, python-docx, Apache Tika fallback
- Cleaning: header/footer removal, page numbers, symbol stripping, whitespace normalization
- Section classification (skills, experience, projects, education, summary, certifications, contact)
- Skill extraction using dictionary + regex
- Experience extraction via date ranges and explicit year patterns
- Local embedding generation (SentenceTransformer local model directory)
- Storage: MongoDB (profile JSON), Qdrant (embeddings)
- Job Description processing (skills, min experience, seniority, embedding)
- Matching via cosine similarity + skill match + experience score composite
- Export endpoint placeholder (extend to generate DOCX/PDF/ZIP)

## Folder Structure
```
resume-matcher/
  backend/
    api/
      __init__.py
      resumes.py
      jd.py
      match.py
    core/
      extractor.py
      cleaner.py
      classifier.py
      skill_extractor.py
      experience_extractor.py
      embedder.py
      db_mongo.py
      db_qdrant.py
    models/
      skill_dict.json
      stopwords.txt
      jd_template.docx (PLACEHOLDER - replace with actual template)
    local_models/
      embeddings/  (place SentenceTransformer model files here)
      ocr/         (optional custom PaddleOCR models)
      llm/         (optional LLM resources if used later)
    main.py
    requirements.txt
  datasets/
    sample_resumes/
    sample_jd/
  README.md
  RUN_STEPS.txt
```

## Prerequisites
- Python 3.9+
- MongoDB running locally (default: mongodb://localhost:27017)
- Qdrant running locally (default: http://localhost:6333) via Docker or binary
- Local embedding model placed in `backend/local_models/embeddings/` (e.g. a SentenceTransformer folder)
- (Optional) Install spaCy model: `python -m spacy download en_core_web_sm`
- (Optional) LibreOffice for DOCX->PDF conversion

## Configuration (Environment Variables)
| Variable | Purpose | Default |
|----------|---------|---------|
| MONGO_URI | Mongo connection string | mongodb://localhost:27017 |
| MONGO_DB | Mongo database name | resume_matcher |
| QDRANT_HOST | Qdrant host | localhost |
| QDRANT_PORT | Qdrant port | 6333 |
| QDRANT_COLLECTION | Qdrant collection name | resumes |
| SPACY_MODEL | spaCy model name | en_core_web_sm |

Set in PowerShell (session):
```
$env:MONGO_URI="mongodb://localhost:27017"
$env:QDRANT_HOST="localhost"
```

## Installation
```
cd resume-matcher/backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm  # optional
```
Place your embedding model directory inside `backend/local_models/embeddings/`.

## Running the API
From `resume-matcher/backend`:
```
uvicorn main:app --reload
```
Visit: http://127.0.0.1:8000/docs for interactive Swagger UI.

## Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /resumes/upload-resume | POST | Upload a single resume file (multipart) |
| /resumes/profile/{employee_id} | GET | Get stored profile JSON |
| /jd/process-jd | POST | Process a job description text |
| /match/run | POST | Run matching JD text vs stored resumes |
| /resumes/export/{employee_id} | GET | Placeholder export (extend for DOCX/PDF/ZIP) |

### Upload Example (curl)
```
curl -X POST -F "file=@sample.pdf" http://localhost:8000/resumes/upload-resume
```

### Matching Example Body
```
{
  "jd_text": "We need a Python engineer with 3 years experience in AWS and React.",
  "top_k": 5
}
```

## Extending Export
Implement DOCX generation using `python-docx` or `docxtpl` (already in requirements). For PDF export on Windows if Word is installed use `docx2pdf`, else call LibreOffice:
```
soffice --headless --convert-to pdf your.docx --outdir output_dir
```
Zip using Python `zipfile`.

## Matching Formula
```
final_score = (skill_score * skill_weight) + (experience_score * exp_weight) + (embedding_score * embed_weight)
```
Weights can be tuned per request.

## Model Placement
- Local sentence embedding model: `backend/local_models/embeddings/`
- PaddleOCR custom models (if any): `backend/local_models/ocr/`
- Optional LLM: `backend/local_models/llm/`
- Skill dictionary: `backend/models/skill_dict.json`
- Sample data: `datasets/sample_resumes/`, `datasets/sample_jd/`

## Troubleshooting
- Empty extraction: ensure Tika installed; scanned PDFs require OCR (PaddleOCR). Increase DPI or use external tools for poor scans.
- Embedding errors: verify local model files (config.json, tokenizer files).
- Qdrant connection refused: start Qdrant container: `docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant`
- Mongo errors: ensure service running (`net start MongoDB` or Docker).

## Next Steps
- Add batch upload endpoint for multiple resumes
- Enhance NER with spaCy for phones/emails/locations
- Implement export generation fully
- Add authentication layer
- Add frontend (React/Vite) consumer

## License
Internal / Proprietary.
