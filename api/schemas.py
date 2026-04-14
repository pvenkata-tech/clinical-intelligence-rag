"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Clinical RAG query request"""
    question: str
    context: str  # In a full app, this context would come from the Vector DB


class QueryResponse(BaseModel):
    """Clinical RAG query response"""
    answer: str
    provider_used: str
