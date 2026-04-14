#!/usr/bin/env python3
"""
Clinical Intelligence RAG - Application Entry Point

This is the root entry point for the application. It imports and runs
the FastAPI application from the api module.

Usage:
    python main.py
    
    Or with specific provider:
    LLM_PROVIDER=ANTHROPIC python main.py
    LLM_PROVIDER=BEDROCK python main.py
"""

from api.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Load configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Run the application
    uvicorn.run(app, host=host, port=port)
