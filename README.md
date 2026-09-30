# Eco-Court AI Assistant - MVP (Milestone 2)

Upload PDF -> extract text per page -> page-aware chunks -> embeddings -> ChromaDB.

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run (two terminals, both from the eco-court-ai/ folder)
```bash
# Terminal 1 - backend
uvicorn backend.app:app --reload

# Terminal 2 - frontend
streamlit run frontend/ui.py
```
Open http://localhost:8501, upload a PDF, click **Process document**, then try the search box.
API docs: http://localhost:8000/docs

## Notes
- First upload downloads the embedding model (~90 MB) - needs internet once.
- Scanned PDFs are flagged (`possibly_scanned`); OCR comes in a later milestone.
- Chunks never cross page boundaries, so page citations stay exact.
- Next: Milestone 3 (question -> retrieval -> LLM answer), Milestone 4 (citations).
