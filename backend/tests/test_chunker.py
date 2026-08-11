from app.ingestion.code_chunker import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_OVERLAP,
    chunk_file,
    create_chunk_id,
)
from app.ingestion.repository_parser import RepositoryFile


def test_small_file_creates_one_chunk():
    repository_file = RepositoryFile(
        path="src/main.py",
        language="python",
        content='print("Hello CodeCompass")',
    )

    chunks = chunk_file(
        file=repository_file,
        project_id="project-123",
    )

    assert len(chunks) == 1
    assert chunks[0].file_path == "src/main.py"
    assert chunks[0].language == "python"
    assert chunks[0].project_id == "project-123"
    assert chunks[0].chunk_index == 0
    assert chunks[0].content == 'print("Hello CodeCompass")'


def test_chunk_ids_are_stable():
    chunk_id_1 = create_chunk_id(
        "project-123",
        "src/main.py",
        0,
    )

    chunk_id_2 = create_chunk_id(
        "project-123",
        "src/main.py",
        0,
    )

    assert chunk_id_1 == chunk_id_2


def test_different_chunks_have_different_ids():
    chunk_id_1 = create_chunk_id(
        "project-123",
        "src/main.py",
        0,
    )

    chunk_id_2 = create_chunk_id(
        "project-123",
        "src/main.py",
        1,
    )

    assert chunk_id_1 != chunk_id_2


def test_large_file_creates_overlapping_chunks():
    content = "A" * 2500

    repository_file = RepositoryFile(
        path="src/main.py",
        language="python",
        content=content,
    )

    chunks = chunk_file(
        file=repository_file,
        project_id="project-123",
        chunk_size=1000,
        overlap=200,
    )

    assert len(chunks) > 1

    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1

    assert len(chunks[0].content) == 1000
    assert len(chunks[1].content) == 1000


def test_invalid_overlap_raises_error():
    repository_file = RepositoryFile(
        path="src/main.py",
        language="python",
        content="print('test')",
    )

    try:
        chunk_file(
            file=repository_file,
            project_id="project-123",
            chunk_size=100,
            overlap=100,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Overlap must be smaller than chunk size."
