"""
Core AI Orchestration Layer

Exports:
- ClinicalRAGOrchestrator: Main RAG pipeline orchestrator
- settings: Application configuration
"""

from core.orchestrator import ClinicalRAGOrchestrator
from core.config import settings

__all__ = ["ClinicalRAGOrchestrator", "settings"]
