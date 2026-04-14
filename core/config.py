import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Application Settings
    APP_NAME = "Clinical Intelligence RAG"
    APP_VERSION = "1.0.0"
    
    # Provider Selection (OPENAI or ANTHROPIC)
    # Default to OPENAI for local development
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "OPENAI").upper()
    
    # AWS Bedrock Settings (if using Bedrock provider)
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID = "amazon.nova-pro-1:0"
    
    # OpenAI Settings
    OPENAI_MODEL_ID = "gpt-4o"
    
    # Anthropic Settings
    ANTHROPIC_MODEL_ID = "claude-opus-4-1-20250805"
    
    # Vector DB
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "clinical-rag")

settings = Settings()