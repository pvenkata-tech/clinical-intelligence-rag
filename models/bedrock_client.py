"""
AWS Bedrock client using long-term API key (BedrockAPIKey format)
Uses boto3 with custom Bedrock API key authentication
"""

import os
import json
import boto3
import base64
from typing import Any, Dict, List, Optional
from core.config import settings


class BedrockChatClient:
    """Bedrock client using AWS Bedrock API key"""
    
    # Models available with Bedrock
    FALLBACK_MODELS = [
        "amazon.nova-pro-1:0",  # Amazon Nova Pro (working)"
        "anthropic.claude-sonnet-4-6-v1:0",  # Claude Sonnet 4.6
        "anthropic.claude-opus-4-1-20250805",  # Claude Opus 4.1
        "anthropic.claude-3-5-sonnet-20241022-v2:0",  # Claude 3.5 Sonnet
    ]
    
    def __init__(self, model_id: Optional[str] = None, api_key: Optional[str] = None):
        self.api_key = api_key
        
        # Try AWS credentials first, then fall back to API key
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        try:
            if aws_access_key and aws_secret_key:
                # Use AWS environment credentials
                self.client = boto3.client(
                    "bedrock-runtime",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
            elif self.api_key:
                # Decode the API key to get credentials
                decoded = base64.b64decode(self.api_key).decode('utf-8')
                # Format: BedrockAPIKey-XXXXX:SECRET
                if ':' in decoded:
                    key_id, secret = decoded.split(':', 1)
                    # Use these as AWS credentials with Bedrock
                    self.client = boto3.client(
                        "bedrock-runtime",
                        region_name=settings.AWS_REGION,
                        aws_access_key_id=key_id,
                        aws_secret_access_key=secret
                    )
                else:
                    raise ValueError("Invalid API key format")
            else:
                raise ValueError("Neither AWS credentials nor API key provided")
        except Exception as e:
            print(f"Warning: Could not initialize Bedrock client: {e}")
            print("Falling back to default credentials...")
            self.client = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)
        
        # Determine which model to use
        if model_id:
            self.model_id = model_id
        else:
            self.model_id = settings.BEDROCK_MODEL_ID
        
        self.working_model = None
    
    def _find_working_model(self) -> str:
        """Try to find a working model from the list"""
        if self.working_model:
            return self.working_model
        
        # Try the configured model first
        models_to_try = [self.model_id] + [m for m in self.FALLBACK_MODELS if m != self.model_id]
        
        for model_id in models_to_try:
            try:
                response = self._invoke_api(
                    model_id=model_id,
                    messages=[{"role": "user", "content": "hi"}],
                    max_tokens=10
                )
                if response:
                    self.working_model = model_id
                    print(f"✓ Found working model: {model_id}")
                    return model_id
            except Exception as e:
                print(f"  Trying {model_id}: {str(e)[:80]}")
                continue
        
        # If no model works, raise error
        raise RuntimeError(
            f"No working Bedrock models found. Tried: {models_to_try}"
        )
    
    def _invoke_api(self, model_id: str, messages: List[Dict[str, Any]], max_tokens: int) -> str:
        """Call AWS Bedrock API"""
        
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-06-01",
                "max_tokens": max_tokens,
                "messages": messages
            })
            
            response = self.client.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_data = json.loads(response["body"].read())
            
            # Extract text from response
            for content_block in response_data.get("content", []):
                if content_block.get("type") == "text":
                    return content_block.get("text", "")
            return ""
        
        except Exception as e:
            raise RuntimeError(f"Bedrock API call failed: {str(e)}")
    
    def invoke(self, messages: List[Dict[str, Any]], max_tokens: int = 1024, temperature: float = 0) -> str:
        """
        Invoke the Bedrock model with messages and return the text response
        
        Args:
            messages: List of message dicts with "role" and "content"
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0-1)
        
        Returns:
            The generated text response
        """
        
        # Find a working model if not yet found
        model_id = self._find_working_model()
        
        try:
            return self._invoke_api(
                model_id=model_id,
                messages=messages,
                max_tokens=max_tokens
            )
        except Exception as e:
            raise RuntimeError(f"Bedrock invocation failed: {str(e)}")



class LangChainBedrockAdapter:
    """Adapter to make BedrockChatClient compatible with LangChain's interface"""
    
    def __init__(self, model_id: Optional[str] = None, api_key: Optional[str] = None):
        self.bedrock_client = BedrockChatClient(model_id=model_id, api_key=api_key)
    
    def invoke(self, input_messages: List[Any], **kwargs) -> Any:
        """
        Invoke the model with LangChain message objects
        
        Args:
            input_messages: List of LangChain message objects
        
        Returns:
            A LangChain AIMessage object
        """
        from langchain_core.messages import AIMessage
        
        # Convert LangChain messages to Bedrock format
        messages = []
        for msg in input_messages:
            if hasattr(msg, 'content'):
                # For HumanMessage, SystemMessage, etc.
                role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.content
                })
        
        # Get response from Bedrock
        text_response = self.bedrock_client.invoke(
            messages=messages,
            max_tokens=kwargs.get('max_tokens', 1024),
            temperature=kwargs.get('temperature', 0)
        )
        
        # Return as LangChain AIMessage
        return AIMessage(content=text_response)
