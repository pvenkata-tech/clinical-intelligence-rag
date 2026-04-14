"""
Pytest configuration and fixtures for Clinical Intelligence RAG tests
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path so tests can import from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def env_vars():
    """Fixture to provide environment variables"""
    return {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "OPENAI"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
    }


@pytest.fixture
def api_base_url():
    """Fixture to provide API base URL"""
    return "http://localhost:8001"


@pytest.fixture
def test_queries():
    """Fixture to provide standard test queries"""
    return [
        {
            "question": "What is hypertension?",
            "context": "Hypertension is a condition where blood pressure is elevated. Normal BP is <120/80 mmHg."
        },
        {
            "question": "How is diabetes managed?",
            "context": "Diabetes is managed through diet, exercise, medications (metformin, insulin), and monitoring blood glucose levels."
        }
    ]
