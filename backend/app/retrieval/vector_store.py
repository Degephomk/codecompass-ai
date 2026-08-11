from pathlib import Path

import chromadb

from app.ingestion.code_chunker import CodeChunk


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_DIR = BASE_DIR / "storage" / "chroma"


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name="code_chunks"
)


def add_chunks(
    chunks: list[CodeChunk],
    embeddings: list[list[float]],
) -> None:
    """Store code chunks and embeddings in ChromaDB."""

    if not chunks:
        return

    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk.content for chunk in chunks],
        metadatas=[
            {
                "project_id": chunk.project_id,
                "file_path": chunk.file_path,
                "language": chunk.language,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ],
    )


def search_chunks(
    query_embedding: list[float],
    project_id: str,
    top_k: int = 5,
) -> dict:
    """Search for relevant chunks within a project."""

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "project_id": project_id,
        },
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    return results
