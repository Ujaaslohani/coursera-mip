from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.auth.dependencies import CurrentUser, require_role_permission
from app.services.retrieval_service import run_query
from app.services.audit_service import log_action

router = APIRouter()


class QueryRequest(BaseModel):
    question_text: str
    top_k: int = 10


class QueryResponse(BaseModel):
    query_id: str
    retrieved_evidence: list[dict]
    agent_plan: dict


@router.post("/api/query", response_model=QueryResponse)
def submit_query(
    payload: QueryRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role_permission("query:run")),
):
    """Accept a unified user question and run permission-aware retrieval across modalities."""
    query, retrieved_evidence, agent_plan = run_query(db, user, payload.question_text, top_k=payload.top_k)
    log_action(db, actor=user.user_id, action="query.run", resource_type="query", resource_id=query.id,
               details={"question": payload.question_text, "evidence_count": len(retrieved_evidence)})
    return QueryResponse(query_id=query.id, retrieved_evidence=retrieved_evidence, agent_plan=agent_plan)
