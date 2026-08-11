from dataclasses import dataclass
import hashlib

from app.ingestion.repository_parser import RepositoryFile


@dataclass
class CodeChunk:
    chunk_id: str
    project_id: str
    file_path: str
    language: str
    chunk_index: int
    content: str


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_OVERLAP = 200


def create_chunk_id(
    project_id: str,
    file_path: str,
    chunk_index: int,
) -> str:
    """
    Create a stable unique identifier for a code chunk.
    """

    value = f"{project_id}:{file_path}:{chunk_index}"

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def chunk_file(
    file: RepositoryFile,
    project_id: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[CodeChunk]:
    """
    Split a repository file into overlapping chunks.
    """

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    content = file.content.strip()

    if not content:
        return []

    chunks = []

    # Small files remain as one chunk.
    if len(content) <= chunk_size:
        chunks.append(
            CodeChunk(
                chunk_id=create_chunk_id(
                    project_id,
                    file.path,
                    0,
                ),
                project_id=project_id,
                file_path=file.path,
                language=file.language,
                chunk_index=0,
                content=content,
            )
        )

        return chunks

    step = chunk_size - overlap
    start = 0
    chunk_index = 0

    while start < len(content):
        end = start + chunk_size

        chunk_content = content[start:end].strip()

        if chunk_content:
            chunks.append(
                CodeChunk(
                    chunk_id=create_chunk_id(
                        project_id,
                        file.path,
                        chunk_index,
                    ),
                    project_id=project_id,
                    file_path=file.path,
                    language=file.language,
                    chunk_index=chunk_index,
                    content=chunk_content,
                )
            )

        start += step
        chunk_index += 1

    return chunks


def chunk_repository(
    files: list[RepositoryFile],
    project_id: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[CodeChunk]:
    """
    Chunk all repository files.
    """

    chunks = []

    for file in files:
        chunks.extend(
            chunk_file(
                file=file,
                project_id=project_id,
                chunk_size=chunk_size,
                overlap=overlap,
            )
        )

    return chunks
