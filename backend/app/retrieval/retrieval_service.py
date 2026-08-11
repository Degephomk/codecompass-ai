from app.retrieval.embedding_service import embedding_service
from app.retrieval.vector_store import search_chunks
from app.retrieval.llm_service import llm_service
from app.retrieval.prompt_builder import build_code_question_prompt


def retrieve_relevant_chunks(
    query: str,
    project_id: str,
    top_k: int = 5,
) -> list[dict]:
    """Retrieve the most relevant code chunks for a query."""

    query_embedding = embedding_service.embed_query(query)

    results = search_chunks(
        query_embedding=query_embedding,
        project_id=project_id,
        top_k=top_k,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        chunks.append(
            {
                "content": document,
                "file_path": metadata["file_path"],
                "language": metadata["language"],
                "chunk_index": metadata["chunk_index"],
                "project_id": metadata["project_id"],
                "distance": distance,
            }
        )

    return chunks


# def answer_question(
#     question: str,
#     project_id: str,
#     top_k: int = 5,
# ) -> dict:
def answer_question(
    question: str,
    project_id: str,
    conversation: list[dict[str, str]] | None = None,
    top_k: int = 5,
) -> dict:

    conversation = conversation or []

    recent_context = conversation[-6:]

    conversation_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_context
    )

    retrieval_query = question

    if conversation_text:
        retrieval_query = (
            f"Previous conversation:\n"
            f"{conversation_text}\n\n"
            f"Current question:\n"
            f"{question}"
        )
    """Retrieve repository context and generate an answer."""

    chunks = retrieve_relevant_chunks(
        query=retrieval_query,
        project_id=project_id,
        top_k=top_k,
    )

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"File: {chunk['file_path']}\n"
            f"Language: {chunk['language']}\n"
            f"Content:\n{chunk['content']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = build_code_question_prompt(
        question=question,
        context=context,
    )

    answer = llm_service.generate(prompt)

    return {
        "answer": answer,
        "sources": [
            {
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "distance": chunk["distance"],
            }
            for chunk in chunks
        ],
    }
