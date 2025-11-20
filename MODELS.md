# Model Acquisition Guide

This file lists recommended models, their purposes, download links, and exact placement paths inside the repository. After downloading, the project can run fully offline.

## 1. Sentence Embedding Model (Primary)
Recommended (fast + good quality):
- Name: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, fast)
  - HuggingFace: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
Alternative higher quality (slower):
- Name: `sentence-transformers/all-mpnet-base-v2` (768-dim)
  - HuggingFace: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
Retrieval-optimized variant:
- Name: `sentence-transformers/multi-qa-MiniLM-L6-cos-v1`
  - HuggingFace: https://huggingface.co/sentence-transformers/multi-qa-MiniLM-L6-cos-v1

Placement Path:
```
resume-matcher/backend/local_models/embeddings/
```
Download Options:
1. Manual: Click "Download repository" on HuggingFace model page; unzip contents into the embeddings folder.
2. Python:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save('resume-matcher/backend/local_models/embeddings')
```
3. Script: Run `python backend/scripts/download_models.py` (after editing SENTENCE_MODEL_NAME environment variable if desired).

NOTE: Changing embedding model changes vector dimension; existing Qdrant collection should be recreated if dimension differs.

## 2. PaddleOCR Models (For Scanned PDFs & Images)
PaddleOCR auto-downloads models by default when you instantiate `PaddleOCR`. To fully offline the setup, pre-download and place them.
Recommended English Models (PP-OCR v4):
- Detection: https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/en_PP-OCRv4_det_infer.tar
- Recognition: https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/en_PP-OCRv4_rec_infer.tar
- Classification: https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_cls_infer.tar (English works fine)
Model list reference: https://github.com/PaddlePaddle/PaddleOCR/wiki/PP-OCR-Model-List#english

Placement Path (extract folders):
```
resume-matcher/backend/local_models/ocr/det/
resume-matcher/backend/local_models/ocr/rec/
resume-matcher/backend/local_models/ocr/cls/
```
Then adjust initializer in `extractor.py` (example):
```python
PaddleOCR(
  use_angle_cls=True,
  lang='en',
  det_model_dir='backend/local_models/ocr/det',
  rec_model_dir='backend/local_models/ocr/rec',
  cls_model_dir='backend/local_models/ocr/cls'
)
```
If you skip manual placement, PaddleOCR will download to `~/.paddleocr` on first run.

## 3. spaCy Model (Optional NER Enhancement)
Model: `en_core_web_sm`
Download:
```
python -m spacy download en_core_web_sm
```
Offline Download:
- Wheels available: https://github.com/explosion/spacy-models/releases
Place wheel locally and install with `pip install en_core_web_sm-*.whl`

## 4. (Optional) Larger NER / Accuracy
- `en_core_web_md` (vectors, better similarity)
- `en_core_web_trf` (transformer-based, slower, highest accuracy)

## 5. (Optional) LLM / Cleaning / Summarization
If you plan to integrate summarization or advanced classification:
- `TheBloke/Mistral-7B-Instruct-v0.2-GGUF` (quantized GGUF for llama.cpp / gpt4all workflows)
- `meta-llama/Llama-3-8B-Instruct` (if license permits and resources available)
Placement Path:
```
resume-matcher/backend/local_models/llm/
```
Integration is not included in current code; you would add a module to call local inference.

## 6. Qdrant
Qdrant isn’t a model—run binary or Docker container.
Docker:
```
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```
Binary downloads: https://qdrant.tech/documentation/guides/installation/

## 7. MongoDB
Community Server (Windows): https://www.mongodb.com/try/download/community
Alternatively run via Docker: `docker run -d -p 27017:27017 mongo:6`

## 8. LibreOffice (DOCX→PDF Conversion)
Download: https://www.libreoffice.org/download/download/
Headless conversion used by CLI: `soffice --headless --convert-to pdf file.docx --outdir output_dir`

## 9. Verification After Download
After placing SentenceTransformer model:
```python
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('resume-matcher/backend/local_models/embeddings')
print(m.get_sentence_embedding_dimension())
```
Should print 384 for all-MiniLM-L6-v2 or 768 for mpnet-base.

## 10. Recreating Qdrant Collection After Model Change
If you switch models (dimension changes), drop the collection:
```python
from qdrant_client import QdrantClient
c = QdrantClient(host='localhost', port=6333)
c.delete_collection('resumes')
```
Then restart API so startup creates a fresh collection.

## 11. Download Script Use
Run:
```
python backend/scripts/download_models.py
```
It will:
- Download chosen SentenceTransformer model.
- (Optionally) Prepare OCR dirs (no direct downloads—links provided).

## 12. Summary of Mandatory vs Optional
| Component | Mandatory | Purpose |
|-----------|-----------|---------|
| SentenceTransformer | YES | Embeddings for resumes & JD |
| PaddleOCR | YES (if scanned PDFs/images) | Text extraction |
| spaCy en_core_web_sm | Optional | NER improvements |
| LLM | Optional | Advanced cleaning/summarization |
| LibreOffice | Optional | DOCX→PDF export |

## 13. Quick One-Line Model Setup (Online Required)
```powershell
python - <<'PY'
from sentence_transformers import SentenceTransformer; m=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); m.save('resume-matcher/backend/local_models/embeddings'); print('Saved model.')
PY
python -m spacy download en_core_web_sm
```

If you need fully offline distribution, include this MODELS.md and a zipped copy of each model directory.

---
Happy building! Bundle everything before sharing: ensure `embeddings/` contains model files and optionally `ocr/` extracted weights.
