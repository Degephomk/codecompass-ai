from pathlib import Path

from app.ingestion.code_chunker import chunk_repository
from app.ingestion.repository_parser import parse_repository
from app.retrieval.embedding_service import embedding_service
from app.retrieval.vector_store import add_chunks


def index_repository(
    project_path: Path,
    project_id: str,
) -> dict:
    """Parse, chunk, embed, and store a repository."""

    files = parse_repository(project_path)

    chunks = chunk_repository(
        files=files,
        project_id=project_id,
    )

    if chunks:
        documents = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = embedding_service.embed_documents(
            documents
        )

        add_chunks(
            chunks=chunks,
            embeddings=embeddings,
        )

    return {
        "file_count": len(files),
        "chunk_count": len(chunks),
    }
