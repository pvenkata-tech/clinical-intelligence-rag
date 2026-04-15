"""
Monitoring & Observability Service
Captures query metrics and sends to LangSmith for tracing
"""

import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics captured for each RAG query"""
    query_id: str
    timestamp: datetime
    question: str
    answer: str
    provider: str
    latency_ms: float
    token_count: int
    retrieved_chunks: int
    error: Optional[str] = None
    
    def to_dict(self):
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d


class MonitoringService:
    """
    Captures RAG query metrics for observability.
    Automatically sends traces to LangSmith via environment variables.
    """
    
    def __init__(self):
        self.langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self.query_history: List[QueryMetrics] = []
        self.max_history = 500
        
        if self.langsmith_enabled:
            logger.info("✅ LangSmith monitoring enabled")
        else:
            logger.info("ℹ️  LangSmith disabled (set LANGCHAIN_TRACING_V2=true to enable)")
    
    def log_query(self, metrics: QueryMetrics) -> None:
        """Log a query execution with metrics"""
        try:
            # Add to in-memory history
            self.query_history.append(metrics)
            
            # Keep history bounded
            if len(self.query_history) > self.max_history:
                self.query_history.pop(0)
            
            logger.info(
                f"📊 Query logged | {metrics.provider} | "
                f"Latency: {metrics.latency_ms:.0f}ms | "
                f"Chunks: {metrics.retrieved_chunks}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics from query history"""
        if not self.query_history:
            return {
                "total_queries": 0,
                "successful_queries": 0,
                "avg_latency_ms": 0,
                "error_rate": 0,
                "providers": {},
            }
        
        total = len(self.query_history)
        errors = sum(1 for q in self.query_history if q.error)
        latencies = [q.latency_ms for q in self.query_history if q.latency_ms]
        
        # Provider breakdown
        providers = {}
        for query in self.query_history:
            if query.provider not in providers:
                providers[query.provider] = {"count": 0, "avg_latency": 0}
            providers[query.provider]["count"] += 1
        
        # Recalculate provider latencies
        for provider in providers:
            p_latencies = [
                q.latency_ms for q in self.query_history 
                if q.provider == provider and q.latency_ms
            ]
            if p_latencies:
                providers[query.provider]["avg_latency"] = sum(p_latencies) / len(p_latencies)
        
        return {
            "total_queries": total,
            "successful_queries": total - errors,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "error_rate": (errors / total * 100) if total > 0 else 0,
            "providers": providers,
        }
    
    def get_recent_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent queries for dashboard display"""
        recent = self.query_history[-limit:]
        return [q.to_dict() for q in reversed(recent)]
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get per-provider performance statistics"""
        if not self.query_history:
            return {}
        
        stats = {}
        for query in self.query_history:
            if query.provider not in stats:
                stats[query.provider] = {
                    "queries": 0,
                    "total_latency": 0,
                    "total_tokens": 0,
                    "errors": 0,
                }
            
            s = stats[query.provider]
            s["queries"] += 1
            s["total_latency"] += query.latency_ms
            s["total_tokens"] += query.token_count
            if query.error:
                s["errors"] += 1
        
        # Calculate averages
        for provider in stats:
            s = stats[provider]
            s["avg_latency"] = s["total_latency"] / s["queries"] if s["queries"] > 0 else 0
            s["avg_tokens"] = s["total_tokens"] / s["queries"] if s["queries"] > 0 else 0
            s["error_rate"] = (s["errors"] / s["queries"] * 100) if s["queries"] > 0 else 0
            del s["total_latency"]
            del s["total_tokens"]
        
        return stats


# Global monitoring service instance
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """Get or create the global monitoring service"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
