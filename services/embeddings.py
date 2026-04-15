from langchain_aws import BedrockEmbeddings
from langchain_openai import OpenAIEmbeddings
from core.config import settings
import os

class EmbeddingService:
    @staticmethod
    def get_embeddings():
        provider = settings.LLM_PROVIDER
        
        if provider == "BEDROCK":
            return BedrockEmbeddings(
                region_name=settings.AWS_REGION,
                model_id="amazon.titan-embed-text-v2:0" # The 2026 standard for Bedrock
            )
        else:
            # Use text-embedding-3-small with dimension 1024 to match Pinecone index
            # Ensure API key is available for OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                dimensions=1024,
                api_key=api_key
            )