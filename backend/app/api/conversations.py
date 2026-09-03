from fastapi import APIRouter, Depends, Query

from app.models import (
    ConversationCreateRequest,
    ConversationResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    InteractionSaveRequest,
    InteractionSaveResponse,
)
from app.services.supabase_service import SupabaseService, get_supabase_service


router = APIRouter(prefix="/api", tags=["conversations"])


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreateRequest,
    service: SupabaseService = Depends(get_supabase_service),
) -> ConversationResponse:
    return service.create_conversation(request)


@router.get("/conversations", response_model=list[ConversationResponse])
def conversations(
    limit: int = Query(default=50, ge=1, le=500),
    service: SupabaseService = Depends(get_supabase_service),
) -> list[ConversationResponse]:
    return service.list_conversations(limit=limit)


@router.get("/conversations/{conversation_id}/messages", response_model=list[dict])
def conversation_messages(
    conversation_id: str,
    service: SupabaseService = Depends(get_supabase_service),
) -> list[dict]:
    return service.get_conversation_messages(conversation_id)


@router.post("/interactions", response_model=InteractionSaveResponse)
def save_interaction(
    request: InteractionSaveRequest,
    service: SupabaseService = Depends(get_supabase_service),
) -> InteractionSaveResponse:
    return service.save_interaction(request)


@router.post("/feedback", response_model=FeedbackResponse)
def save_feedback(
    request: FeedbackCreateRequest,
    service: SupabaseService = Depends(get_supabase_service),
) -> FeedbackResponse:
    return service.save_feedback(request)
