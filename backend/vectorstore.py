import chromadb
from .config import CHROMA_DIR, COLLECTION_NAME
from .embeddings import embed_texts

_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
)


def add_chunks(doc_id: str, filename: str, chunks: list[dict]) -> None:
    if not chunks:
        return
    texts = [c["text"] for c in chunks]
    _collection.add(
        ids=[f"{doc_id}_{c['chunk_index']}" for c in chunks],
        documents=texts,
        embeddings=embed_texts(texts),
        metadatas=[{"doc_id": doc_id, "filename": filename,
                    "page": c["page"], "chunk_index": c["chunk_index"]} for c in chunks],
    )


def search(query: str, k: int = 5, doc_id: str | None = None) -> list[dict]:
    res = _collection.query(
        query_embeddings=embed_texts([query]),
        n_results=k,
        where={"doc_id": doc_id} if doc_id else None,
    )
    hits = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": text, "filename": meta["filename"], "page": meta["page"],
                     "chunk_index": meta["chunk_index"], "score": round(1 - dist, 4)})
    return hits


def count() -> int:
    return _collection.count()
