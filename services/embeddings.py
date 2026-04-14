from langchain_aws import BedrockEmbeddings
from langchain_openai import OpenAIEmbeddings
from core.config import settings

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
            return OpenAIEmbeddings(model="text-embedding-3-small")