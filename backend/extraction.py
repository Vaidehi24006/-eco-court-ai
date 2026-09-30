import re
import pymupdf  # PyMuPDF


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"-\n(?=[a-z])", "", text)        # join words hyphenated at line end
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pages(pdf_path: str) -> list[dict]:
    """Return [{'page': 1, 'text': '...'}, ...] - page numbers start at 1."""
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            pages.append({"page": i, "text": clean_text(page.get_text())})
    return pages


def looks_scanned(pages: list[dict], threshold: int) -> bool:
    if not pages:
        return True
    avg = sum(len(p["text"]) for p in pages) / len(pages)
    return avg < threshold
