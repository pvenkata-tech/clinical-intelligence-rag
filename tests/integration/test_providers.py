#!/usr/bin/env python3
"""
Integration Test: LLM Provider Support
Tests all supported LLM providers (OpenAI, Anthropic, Bedrock)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

from core.config import settings
from core.orchestrator import ClinicalRAGOrchestrator

# Test queries
TEST_QUERIES = [
    {
        "question": "What is hypertension?",
        "context": "Hypertension is a condition where blood pressure is elevated. Normal BP is <120/80 mmHg."
    },
    {
        "question": "How is diabetes managed?",
        "context": "Diabetes is managed through diet, exercise, medications (metformin, insulin), and monitoring blood glucose levels."
    }
]


def check_provider_dependencies():
    """Check which providers have required API keys/credentials"""
    print("\n" + "=" * 80)
    print("PROVIDER DEPENDENCY CHECK")
    print("=" * 80)

    providers = {
        "OPENAI": {
            "required": ["OPENAI_API_KEY"],
            "env_vars": ["OPENAI_API_KEY"]
        },
        "ANTHROPIC": {
            "required": ["ANTHROPIC_API_KEY"],
            "env_vars": ["ANTHROPIC_API_KEY"]
        },
        "BEDROCK": {
            "required": ["AWS Credentials"],
            "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
        }
    }

    available = []
    missing = []

    for provider, deps in providers.items():
        env_vars = deps["env_vars"]
        has_all = all(os.getenv(var) for var in env_vars)
        
        status = "✓ AVAILABLE" if has_all else "✗ MISSING"
        print(f"\n{provider:<12} {status}")
        print(f"  Requires: {', '.join(deps['required'])}")
        
        for var in env_vars:
            val = "SET" if os.getenv(var) else "NOT SET"
            print(f"    - {var:<25} {val}")
        
        if has_all:
            available.append(provider)
        else:
            missing.append(provider)

    return available, missing


def test_provider(provider_name: str):
    """Test a specific provider"""
    print(f"\n{'=' * 80}")
    print(f"TESTING PROVIDER: {provider_name}")
    print(f"{'=' * 80}")
    
    # Set provider
    os.environ["LLM_PROVIDER"] = provider_name
    
    try:
        # Initialize orchestrator
        print(f"\n[STEP 1] Initializing orchestrator...")
        orchestrator = ClinicalRAGOrchestrator()
        print(f"✓ Orchestrator initialized")
        print(f"  Model: {orchestrator.model.__class__.__name__}")
        
        # Run test query
        print(f"\n[STEP 2] Running test query...")
        for i, test_case in enumerate(TEST_QUERIES, 1):
            question = test_case["question"]
            context = test_case["context"]
            
            print(f"\n  Query {i}: {question}")
            print(f"  Context: {context[:60]}...")
            
            answer = orchestrator.query(question, context)
            print(f"  ✓ Response: {answer[:100]}...")
        
        print(f"\n✓✓✓ {provider_name} TEST PASSED ✓✓✓")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    print("\n" + "=" * 80)
    print("CLINICAL INTELLIGENCE RAG - MULTI-PROVIDER TEST")
    print("=" * 80)
    print(f"App: {settings.APP_NAME}")
    print(f"Version: {settings.APP_VERSION}")
    
    # Check dependencies
    available, missing = check_provider_dependencies()
    
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"Available providers: {', '.join(available) if available else 'NONE'}")
    print(f"Missing providers: {', '.join(missing) if missing else 'NONE'}")
    
    # Test available providers
    if available:
        results = {}
        for provider in available:
            results[provider] = test_provider(provider)
        
        # Final results
        print(f"\n{'=' * 80}")
        print("FINAL RESULTS")
        print(f"{'=' * 80}")
        for provider, passed in results.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{provider:<12} {status}")
        
        passed_count = sum(1 for p in results.values() if p)
        total_count = len(results)
        print(f"\nTotal: {passed_count}/{total_count} providers working")
    else:
        print("\n✗ No providers available with configured API keys")
        print("\nTo test providers, add these to your .env file:")
        print("  OPENAI_API_KEY=sk-.....")
        print("  ANTHROPIC_API_KEY=sk-ant-.....")
        print("  AWS_ACCESS_KEY_ID=.....")
        print("  AWS_SECRET_ACCESS_KEY=.....")


if __name__ == "__main__":
    main()
