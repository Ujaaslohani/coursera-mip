from dataclasses import asdict

from sqlalchemy.orm import Session

from app.database.models import Query
from app.auth.dependencies import CurrentUser
from app.services.lifecycle_service import mark_segments_retrieved
from ai.retrieval.retriever import retrieve
from ai.agents.retrieval_planner import plan
from ai.agents.evidence_ranker import rank


def run_query(db: Session, user: CurrentUser, question_text: str, top_k: int = 10) -> tuple[Query, list[dict], dict]:
    query = Query(user_id=user.user_id, question_text=question_text)
    db.add(query)
    db.commit()
    db.refresh(query)

    # Agent pipeline, per doc §7.5: a planner decides search strategy before
    # anything is searched, retrieval enforces access control before evidence
    # ever reaches synthesis (doc §5.4), and a ranker re-orders for
    # cross-modal diversity rather than raw similarity alone.
    query_plan = plan(question_text, default_top_k=top_k)
    evidence = retrieve(db, query_plan["search_terms"], user.permitted_sources, top_k=query_plan["top_k"])
    ranked_evidence = rank(evidence)[: query_plan["top_k"]]
    retrieved_evidence = [asdict(e) for e in ranked_evidence]

    mark_segments_retrieved(db, [e["segment_id"] for e in retrieved_evidence])

    return query, retrieved_evidence, query_plan
