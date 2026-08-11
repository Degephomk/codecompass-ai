from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.retrieval.retrieval_service import answer_question


router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


# class QueryRequest(BaseModel):
#     project_id: str = Field(..., min_length=1)
#     question: str = Field(..., min_length=1)
class QueryRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    conversation: list[dict[str, str]] = Field(default_factory=list)


class Source(BaseModel):
    file_path: str
    language: str
    distance: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


@router.post("/", response_model=QueryResponse)
def query_repository(request: QueryRequest):
    """Answer a question about an indexed repository."""

    try:
        result = answer_question(
            question=request.question,
            project_id=request.project_id,
            conversation=request.conversation,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to answer the repository question.",
        ) from exc
