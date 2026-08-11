from app.ingestion.code_chunker import CodeChunk
from app.retrieval.embedding_service import embedding_service
from app.retrieval.retrieval_service import retrieve_relevant_chunks
from app.retrieval.vector_store import add_chunks


def test_retrieve_relevant_chunk():
    project_id = "test-retrieval-project"

    chunks = [
        CodeChunk(
            chunk_id="retrieval-python",
            project_id=project_id,
            file_path="src/main.py",
            language="python",
            chunk_index=0,
            content='def hello():\n    print("Hello CodeCompass")',
        ),
        CodeChunk(
            chunk_id="retrieval-readme",
            project_id=project_id,
            file_path="README.md",
            language="markdown",
            chunk_index=0,
            content="# CodeCompass Test Repository",
        ),
    ]

    embeddings = embedding_service.embed_documents(
        [chunk.content for chunk in chunks]
    )

    add_chunks(chunks, embeddings)

    results = retrieve_relevant_chunks(
        query="Where is the Python hello function?",
        project_id=project_id,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["file_path"] == "src/main.py"
    assert results[0]["language"] == "python"


def test_retrieval_is_isolated_by_project():
    project_a = "project-a"
    project_b = "project-b"

    chunks = [
        CodeChunk(
            chunk_id="project-a-chunk",
            project_id=project_a,
            file_path="src/auth.py",
            language="python",
            chunk_index=0,
            content="def authenticate_user(): return True",
        ),
        CodeChunk(
            chunk_id="project-b-chunk",
            project_id=project_b,
            file_path="src/database.py",
            language="python",
            chunk_index=0,
            content="def connect_database(): return database",
        ),
    ]

    embeddings = embedding_service.embed_documents(
        [chunk.content for chunk in chunks]
    )

    add_chunks(chunks, embeddings)

    results = retrieve_relevant_chunks(
        query="How does user authentication work?",
        project_id=project_a,
        top_k=5,
    )

    assert len(results) == 1
    assert results[0]["project_id"] == project_a
    assert results[0]["file_path"] == "src/auth.py"
