"""
Monitoring API Routes
Expose query metrics and observability endpoints
"""

from fastapi import APIRouter
from services.monitoring import get_monitoring_service

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/stats")
async def get_stats():
    """Get aggregated statistics from query history"""
    monitoring = get_monitoring_service()
    return monitoring.get_stats()


@router.get("/queries")
async def get_recent_queries(limit: int = 50):
    """Get recent queries with metrics"""
    monitoring = get_monitoring_service()
    return {
        "queries": monitoring.get_recent_queries(limit=limit),
        "total_tracked": len(monitoring.query_history)
    }


@router.get("/providers")
async def get_provider_stats():
    """Compare performance across LLM providers"""
    monitoring = get_monitoring_service()
    return monitoring.get_provider_stats()


@router.get("/status")
async def monitoring_status():
    """Check monitoring system status"""
    monitoring = get_monitoring_service()
    return {
        "status": "operational",
        "langsmith_enabled": monitoring.langsmith_enabled,
        "queries_tracked": len(monitoring.query_history),
        "langsmith_dashboard": "https://smith.langchain.com" if monitoring.langsmith_enabled else None,
    }
