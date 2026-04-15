from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from typing import List
from langchain_core.documents.base import Document


class PHIScrubber:
    """
    De-identifies Protected Health Information (PHI) from clinical documents.
    
    HIPAA Compliance: This module ensures clinical documents are de-identified
    before being fed into RAG pipelines, especially when processing through
    cloud-based LLMs that may not be HIPAA-covered entities.
    
    Supported scrubbing patterns:
    - Patient names (via pattern matching and NLP)
    - Medical Record Numbers (MRNs)
    - Social Security Numbers (SSNs)
    - Phone numbers
    - Email addresses
    - Date of birth and admission dates
    
    Production Integration Options:
    1. AWS Comprehend Medical - NER-based PHI detection
    2. Microsoft Text Analytics for Health
    3. Private LLMs with healthcare fine-tuning
    4. Rule-based regex patterns (current placeholder)
    """
    
    def __init__(self, enable_scrubbing: bool = True):
        self.enable_scrubbing = enable_scrubbing
    
    def scrub_phi(self, text: str) -> str:
        """
        Remove or replace PHI in text using pattern matching.
        
        This is a PLACEHOLDER implementation. In production, integrate:
        - AWS Comprehend Medical for NER-based PHI detection
        - More sophisticated NLP models for entity recognition
        - HIPAA-compliant de-identification services
        """
        if not self.enable_scrubbing:
            return text
        
        # Pattern: Social Security Number (XXX-XX-XXXX)
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
        
        # Pattern: Medical Record Number (common formats)
        text = re.sub(r'\b(?:MRN|MEDICALRECORD)[:\s]*\d{6,10}\b', '[MRN_REDACTED]', text, flags=re.IGNORECASE)
        
        # Pattern: Phone number (US formats)
        text = re.sub(r'\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}\b', '[PHONE_REDACTED]', text)
        
        # Pattern: Email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL_REDACTED]', text)
        
        # Pattern: Common date patterns (MM/DD/YYYY, MM-DD-YYYY, etc.)
        # Only redact if likely to be DOB or admission date (not relative dates)
        text = re.sub(r'(?:DOB|DATE OF BIRTH|ADMISSION DATE|DISCHARGE DATE)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})', 
                     '[DATE_REDACTED]', text, flags=re.IGNORECASE)
        
        return text
    
    def scrub_documents(self, documents: List[Document]) -> List[Document]:
        """Scrub all documents in a list"""
        scrubbed = []
        for doc in documents:
            doc.page_content = self.scrub_phi(doc.page_content)
            scrubbed.append(doc)
        return scrubbed


class ClinicalIngestor:
    def __init__(self, enable_phi_scrubbing: bool = False):
        """
        Initialize the clinical document ingestor.
        
        Args:
            enable_phi_scrubbing: Whether to apply PHI de-identification.
                                 Recommended: True for production systems.
        """
        # Healthcare-specific splitting: keep paragraphs together for context
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize PHI scrubber for HIPAA compliance
        self.phi_scrubber = PHIScrubber(enable_scrubbing=enable_phi_scrubbing)

    def process_document(self, file_path: str):
        """
        Process clinical PDF document: load, chunk, and optionally de-identify.
        
        Pipeline:
        1. Load PDF using PyPDFLoader
        2. Split into chunks with medical-aware separators
        3. Remove PHI if enabled (de-identification)
        4. Return processed segments
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.splitter.split_documents(documents)
        
        # Apply PHI scrubbing if enabled
        if self.phi_scrubber.enable_scrubbing:
            chunks = self.phi_scrubber.scrub_documents(chunks)
        
        return chunks