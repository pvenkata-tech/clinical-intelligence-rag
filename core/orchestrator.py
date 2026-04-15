import os
import time
import uuid
from datetime import datetime
from models.factory import ModelFactory
from core.ingestion import ClinicalIngestor
from core.config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.monitoring import get_monitoring_service, QueryMetrics

class ClinicalRAGOrchestrator:
    def __init__(self):
        # Initialize LangChain tracing if enabled
        if settings.LANGCHAIN_TRACING_ENABLED:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if settings.LANGCHAIN_API_KEY:
                os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
            print("🔍 LangChain tracing enabled - traces will be sent to LangSmith")
        
        # Initialize the model using our flexible factory
        self.model = ModelFactory.get_model()
        self.ingestor = ClinicalIngestor()
        self.parser = StrOutputParser()

    def get_rag_chain(self, context: str):
        """
        Creates a chain that uses retrieved medical context to answer questions.
        This is the core RAG logic.
        """
        template = """
        You are a Senior Medical AI Assistant. Use the following pieces of retrieved 
        context to answer the user's question. If the answer is not in the context, 
        say that you don't know based on the provided data.
        
        Context: {context}
        
        Question: {question}
        
        Answer (Be professional and cite context if possible):
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # The LCEL (LangChain Expression Language) Chain
        return prompt | self.model | self.parser

    def query(self, question: str, context: str):
        """Execute RAG query with automatic metric capture"""
        query_id = str(uuid.uuid4())
        start_time = time.time()
        answer = ""
        error = None
        
        try:
            chain = self.get_rag_chain(context)
            answer = chain.invoke({"question": question, "context": context})
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            token_count = len(question.split()) + len(answer.split()) + len(context.split()) // 4
            retrieved_chunks = context.count("---") + 1 if context else 0
            
            # Log to monitoring service
            metrics = QueryMetrics(
                query_id=query_id,
                timestamp=datetime.now(),
                question=question,
                answer=answer,
                provider=settings.LLM_PROVIDER,
                latency_ms=latency_ms,
                token_count=token_count,
                retrieved_chunks=retrieved_chunks,
                error=None,
            )
            get_monitoring_service().log_query(metrics)
            
            return answer
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error = str(e)
            
            # Log error metrics
            metrics = QueryMetrics(
                query_id=query_id,
                timestamp=datetime.now(),
                question=question,
                answer="",
                provider=settings.LLM_PROVIDER,
                latency_ms=latency_ms,
                token_count=0,
                retrieved_chunks=0,
                error=error,
            )
            get_monitoring_service().log_query(metrics)
            raise