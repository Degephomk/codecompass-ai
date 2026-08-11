from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingService:
    """Generate vector embeddings for repository chunks."""

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_documents(
        self,
        documents: list[str],
    ) -> list[list[float]]:
        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        return embedding.tolist()


embedding_service = EmbeddingService()
