from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from models.bedrock_client import LangChainBedrockAdapter
from core.config import settings
import os


class ModelFactory:
    @staticmethod
    def get_model():
        provider = settings.LLM_PROVIDER
        
        # Try the configured provider first
        if provider == "BEDROCK":
            try:
                # Check for AWS credentials
                aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
                aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                if not aws_access_key or not aws_secret_key:
                    raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY not found in environment")
                
                adapter = LangChainBedrockAdapter(
                    model_id=settings.BEDROCK_MODEL_ID,
                    api_key=None
                )
                # Test instantiation by finding a working model
                adapter.bedrock_client._find_working_model()
                return adapter
            except Exception as e:
                print(f"⚠️ Bedrock unavailable ({str(e)[:80]}). Falling back to Anthropic...")
                return ChatAnthropic(
                    model=settings.ANTHROPIC_MODEL_ID,
                    temperature=0
                )
        elif provider == "OPENAI":
            return ChatOpenAI(
                model=settings.OPENAI_MODEL_ID, 
                temperature=0
            )
        elif provider == "ANTHROPIC":
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL_ID, 
                temperature=0
            )
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")