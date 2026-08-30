from fastapi import APIRouter, Depends

from app.models import DashboardSummaryResponse, SupabaseHealthResponse, SupabaseTablesResponse
from app.services.supabase_service import SupabaseService, get_supabase_service


router = APIRouter(prefix="/api", tags=["supabase"])


@router.get("/supabase/health", response_model=SupabaseHealthResponse)
def supabase_health(
    service: SupabaseService = Depends(get_supabase_service),
) -> SupabaseHealthResponse:
    return service.health()


@router.get("/supabase/tables", response_model=SupabaseTablesResponse)
def supabase_tables(
    service: SupabaseService = Depends(get_supabase_service),
) -> SupabaseTablesResponse:
    return service.list_tables()


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    service: SupabaseService = Depends(get_supabase_service),
) -> DashboardSummaryResponse:
    return service.dashboard_summary()
