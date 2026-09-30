from functools import lru_cache
from sentence_transformers import SentenceTransformer
from .config import EMBED_MODEL


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    # First call downloads the model (~90 MB) and caches it locally.
    return SentenceTransformer(EMBED_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    vecs = get_model().encode(texts, batch_size=32, normalize_embeddings=True,
                              show_progress_bar=False)
    return vecs.tolist()
