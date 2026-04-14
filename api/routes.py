"""
API Routes for Clinical Intelligence RAG
Defines all FastAPI endpoints
"""

from fastapi import APIRouter, HTTPException
from api.schemas import QueryRequest, QueryResponse
from core.orchestrator import ClinicalRAGOrchestrator
from core.config import settings

router = APIRouter()

# Initialize the Orchestrator (shared across routes)
_orchestrator = ClinicalRAGOrchestrator()


@router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "provider": settings.LLM_PROVIDER,
        "version": settings.APP_VERSION
    }


@router.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Process a medical question using the RAG pipeline
    
    Args:
        request: QueryRequest containing question and context
        
    Returns:
        QueryResponse with answer and provider info
    """
    try:
        # Using the orchestrator to get the answer
        answer = _orchestrator.query(request.question, request.context)
        return QueryResponse(
            answer=answer,
            provider_used=settings.LLM_PROVIDER
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
