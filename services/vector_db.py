from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from services.embeddings import EmbeddingService
from core.config import settings
import os
from typing import List, Optional
from langchain_core.documents.base import Document


class ContextualCompressor:
    """
    Compresses and re-ranks retrieved documents to reduce noise and token costs.
    
    This is critical for clinical RAG where retrieved chunks often contain:
    - Header/footer information
    - Irrelevant vital signs
    - Duplicate metadata
    
    The compressor uses a lightweight scoring mechanism to identify the most
    clinically relevant segments before they hit the expensive LLM.
    """
    
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "ANTHROPIC")
    
    def score_relevance(self, query: str, doc: Document) -> float:
        """
        Score a document's relevance to the query using keyword matching and heuristics.
        This is a lightweight approach that doesn't require an LLM call.
        
        In production, you could integrate reranker models like:
        - BGE-reranker (Hugging Face)
        - Cohere Rerank API
        - AWS Comprehend Medical
        """
        content = doc.page_content.lower()
        query_terms = query.lower().split()
        
        # Calculate term frequency score
        score = 0.0
        for term in query_terms:
            if term in content:
                score += content.count(term) * 0.1
        
        # Boost score for clinical keywords
        clinical_keywords = [
            "diagnosis", "treatment", "patient", "symptom", "medication",
            "procedure", "clinical", "medical", "disease", "condition",
            "oxygen saturation", "vital signs", "blood pressure", "heart rate"
        ]
        
        for keyword in clinical_keywords:
            if keyword in content:
                score += 0.05
        
        # Penalize noise patterns
        noise_patterns = ["page ", "---", "footer", "header", "ref:", "fig."]
        for pattern in noise_patterns:
            if pattern in content:
                score -= 0.1
        
        return max(0.0, score)
    
    def compress(self, query: str, docs: List[Document], min_length: int = 100) -> List[Document]:
        """
        Re-rank and optionally compress retrieved documents.
        
        Returns documents sorted by relevance score, with noisy segments filtered.
        """
        # Score and filter documents
        scored_docs = [
            (self.score_relevance(query, doc), doc)
            for doc in docs
        ]
        
        # Sort by relevance score (descending)
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Filter documents below noise threshold
        compressed = [
            doc for score, doc in scored_docs
            if score > 0.0 and len(doc.page_content) >= min_length
        ]
        
        return compressed if compressed else [doc for _, doc in scored_docs[:len(docs)]]


class VectorStoreManager:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embeddings = EmbeddingService.get_embeddings()
        self.compressor = ContextualCompressor()

    def get_vector_store(self):
        return PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )

    def add_documents(self, documents):
        """Adds processed LangChain documents to Pinecone"""
        vector_store = self.get_vector_store()
        return vector_store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 4, enable_compression: bool = True):
        """
        Retrieves the most relevant clinical context.
        
        Args:
            query: The clinical question or prompt
            k: Number of documents to retrieve
            enable_compression: Whether to apply contextual compression
        
        Returns:
            List of compressed and re-ranked Document objects
        """
        vector_store = self.get_vector_store()
        docs = vector_store.similarity_search(query, k=k)
        
        # Apply contextual compression to reduce noise and token costs
        if enable_compression and docs:
            docs = self.compressor.compress(query, docs)
        
        return docs