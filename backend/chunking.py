def _split_page(text: str, size: int, overlap: int) -> list[str]:
    """Split one page into ~size-char pieces, preferring paragraph/sentence breaks."""
    if len(text) <= size:
        return [text] if text else []

    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            window = text[start:end]
            # look for the best break point in the last 30% of the window
            min_pos = int(size * 0.7)
            para = window.rfind("\n\n", min_pos)
            sent = max(window.rfind(". ", min_pos), window.rfind(".\n", min_pos))
            cut = para if para != -1 else sent
            if cut != -1:
                end = start + cut + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_pages(pages: list[dict], size: int = 1000, overlap: int = 150) -> list[dict]:
    """Chunk page by page so every chunk belongs to exactly ONE page.
    This keeps page-level citations exact (Milestone 4)."""
    chunks = []
    for p in pages:
        for j, piece in enumerate(_split_page(p["text"], size, overlap)):
            chunks.append({"page": p["page"], "chunk_in_page": j, "text": piece})
    for idx, c in enumerate(chunks):
        c["chunk_index"] = idx
    return chunks
