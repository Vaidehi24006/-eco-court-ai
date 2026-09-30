import os
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from . import vectorstore
from .chunking import chunk_pages
from .config import (CHUNK_OVERLAP, CHUNK_SIZE, MAX_FILE_MB, SCANNED_THRESHOLD,
                     TOP_K, UPLOAD_DIR)
from .extraction import extract_pages, looks_scanned
from .llm import LLMError
from .rag import answer_question

app = FastAPI(title="Eco-Court AI - MVP")


class AskRequest(BaseModel):
    question: str
    doc_id: str | None = None
    k: int = TOP_K


@app.get("/health")
def health():
    return {"status": "ok", "chunks_in_db": vectorstore.count()}


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # --- validate ---
    name = os.path.basename(file.filename or "document.pdf")
    if not name.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed.")
    data = await file.read()
    if len(data) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(413, f"File larger than {MAX_FILE_MB} MB.")
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "File is not a valid PDF.")

    # --- save under a random id (never trust the user's filename on disk) ---
    doc_id = uuid.uuid4().hex[:12]
    path = UPLOAD_DIR / f"{doc_id}.pdf"
    path.write_bytes(data)

    # --- extract -> chunk -> embed -> store ---
    try:
        pages = extract_pages(str(path))
    except Exception as e:
        path.unlink(missing_ok=True)
        raise HTTPException(400, f"Could not read PDF: {e}")

    scanned = looks_scanned(pages, SCANNED_THRESHOLD)
    chunks = chunk_pages(pages, CHUNK_SIZE, CHUNK_OVERLAP)
    if chunks:
        vectorstore.add_chunks(doc_id, name, chunks)

    return {
        "doc_id": doc_id,
        "filename": name,
        "num_pages": len(pages),
        "num_chunks": len(chunks),
        "possibly_scanned": scanned,
        "preview": "\n\n".join(p["text"] for p in pages[:2])[:2000],
        "sample_chunks": chunks[:5],
    }


@app.get("/search")
def search(q: str, k: int = 5, doc_id: str | None = None):
    if not q.strip():
        raise HTTPException(400, "Query is empty.")
    return {"query": q, "results": vectorstore.search(q, k=min(k, 20), doc_id=doc_id)}


@app.post("/ask")
def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question is empty.")
    if len(req.question) > 1000:
        raise HTTPException(400, "Question is too long (max 1000 characters).")
    try:
        return answer_question(req.question.strip(), req.doc_id, min(req.k, 10))
    except LLMError as e:
        raise HTTPException(502, str(e))