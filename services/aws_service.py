"""
AWS Utilities Service
Manages AWS credentials and shared Bedrock session logic
"""

import os
import boto3
from typing import Optional


class AWSService:
    """
    Centralized AWS service for credentials and session management
    Prevents creating multiple boto3 clients across the application
    """
    
    _instance = None  # Singleton pattern
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.session_token = os.getenv("AWS_SESSION_TOKEN")
        self._bedrock_client = None
    
    @property
    def bedrock_client(self):
        """Get or create Bedrock runtime client"""
        if self._bedrock_client is None:
            kwargs = {
                "region_name": self.region,
            }
            if self.access_key and self.secret_key:
                kwargs["aws_access_key_id"] = self.access_key
                kwargs["aws_secret_access_key"] = self.secret_key
            if self.session_token:
                kwargs["aws_session_token"] = self.session_token
                
            self._bedrock_client = boto3.client("bedrock-runtime", **kwargs)
        return self._bedrock_client
    
    def has_credentials(self) -> bool:
        """Check if AWS credentials are configured"""
        return bool(self.access_key and self.secret_key)
