import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_MB = 50
CHUNK_SIZE = 1000        # characters (~200 words)
CHUNK_OVERLAP = 150      # characters shared between neighbouring chunks
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # small, free, runs on CPU
COLLECTION_NAME = "legal_chunks"
SCANNED_THRESHOLD = 50   # avg chars/page below this => probably a scanned PDF

# ---- Milestone 3: LLM ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
TOP_K = 5                # how many chunks we give the LLM
MIN_SCORE = 0.20         # below this similarity we say "insufficient information"