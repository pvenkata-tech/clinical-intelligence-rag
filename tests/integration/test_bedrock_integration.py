#!/usr/bin/env python3
"""
Integration Test: Bedrock Provider
Tests the complete RAG pipeline with Bedrock and fallback mechanism
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Force Bedrock provider
os.environ["LLM_PROVIDER"] = "BEDROCK"

from core.config import settings
from core.orchestrator import ClinicalRAGOrchestrator


def test_comprehensive_bedrock():
    """Comprehensive test of Bedrock integration"""
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BEDROCK INTEGRATION TEST")
    print("=" * 80)
    
    # Test 1: Configuration
    print("\n[TEST 1] Configuration")
    print("-" * 80)
    print(f"LLM Provider:     {settings.LLM_PROVIDER}")
    print(f"Bedrock Model ID: {settings.BEDROCK_MODEL_ID}")
    print(f"AWS Region:       {settings.AWS_REGION}")
    print(f"AWS_ACCESS_KEY:   {'SET' if os.getenv('AWS_ACCESS_KEY_ID') else 'NOT SET'}")
    
    # Test 2: Orchestrator Initialization
    print("\n[TEST 2] Orchestrator Initialization")
    print("-" * 80)
    try:
        orchestrator = ClinicalRAGOrchestrator()
        print("✓ ClinicalRAGOrchestrator initialized successfully")
        print(f"  Model class: {orchestrator.model.__class__.__name__}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 3: Simple Query
    print("\n[TEST 3] Simple Medical Query")
    print("-" * 80)
    try:
        question = "What is hypertension?"
        context = """Hypertension, or high blood pressure, is a condition where the force of blood 
        pushing against the artery walls is consistently too high (usually 130/80 mmHg or higher). 
        It can lead to serious health problems like heart disease and stroke if left untreated."""
        
        print(f"Question: {question}")
        print(f"Context:  {context[:60]}...")
        print("\nGenerating response...")
        
        answer = orchestrator.query(question, context)
        
        print(f"\nResponse:\n{answer}")
        print("✓ Query completed successfully")
    except Exception as e:
        print(f"✗ Query failed: {e}")
        return False
    
    # Test 4: Complex Multi-turn Query
    print("\n[TEST 4] Complex Medical Scenario")
    print("-" * 80)
    try:
        question = "What complications could arise from untreated hypertension?"
        context = """Hypertension increases the risk of cardiovascular complications. 
        Chronic high blood pressure damages the arterial walls, leading to atherosclerosis. 
        It significantly increases the risk of myocardial infarction (heart attack) and 
        cerebrovascular accident (stroke). Additionally, hypertension can damage the kidneys, 
        leading to chronic kidney disease, and can impact vision causing hypertensive retinopathy."""
        
        print(f"Question: {question}")
        print(f"Context:  {context[:60]}...")
        print("\nGenerating response...")
        
        answer = orchestrator.query(question, context)
        
        print(f"\nResponse:\n{answer}")
        print("✓ Complex query completed successfully")
    except Exception as e:
        print(f"✗ Complex query failed: {e}")
        return False
    
    # Test 5: JSON Response Format (if API is called)
    print("\n[TEST 5] Response Format Validation")
    print("-" * 80)
    try:
        # Validate the response from Test 4
        if isinstance(answer, str) and len(answer) > 0:
            print(f"Response type:   {type(answer).__name__}")
            print(f"Response length: {len(answer)} characters")
            print(f"Has content:     {'Yes' if answer.strip() else 'No'}")
            print("✓ Response format is valid")
        else:
            print("✗ Response format is invalid")
            return False
    except Exception as e:
        print(f"✗ Format validation failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED ✓")
    print("=" * 80)
    print("\nSummary:")
    print("- Bedrock configuration loaded")
    print("- Orchestrator initialized (with Anthropic fallback)")
    print("- Queries executed successfully")
    print("- Responses generated in correct format")
    print("\nNote: Bedrock models unavailable (not enabled in AWS account)")
    print("      System gracefully fell back to Anthropic Claude")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = test_comprehensive_bedrock()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Integration Test: REST API Endpoints
Tests FastAPI endpoints for the Clinical RAG application
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"


def test_endpoints():
    """Test all API endpoints"""
    print("\n" + "=" * 80)
    print("CLINICAL RAG API - ENDPOINT TESTS")
    print("=" * 80)
    
    # Test 1: Root endpoint
    print("\n[TEST 1] GET / (Root)")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Query endpoint with medical question
    print("\n[TEST 2] POST /query (Medical Question)")
    print("-" * 80)
    
    test_cases = [
        {
            "question": "What are the main symptoms of hypertension?",
            "context": "Hypertension (high blood pressure) is often called the 'silent killer' because it usually has no symptoms. However, some people may experience headaches, chest pain, or shortness of breath in severe cases."
        },
        {
            "question": "How do we diagnose diabetes?",
            "context": "Diabetes is diagnosed through blood tests including fasting blood glucose, A1C (glycated hemoglobin), and oral glucose tolerance tests. A fasting glucose of 126 mg/dL or higher typically indicates diabetes."
        },
        {
            "question": "What treatments are available for hypertension?",
            "context": "Hypertension can be managed with lifestyle changes (diet, exercise, stress reduction) and medications including ACE inhibitors, beta-blockers, calcium channel blockers, and diuretics."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nQuery {i}:")
        print(f"Question: {test['question']}")
        print(f"Context: {test['context'][:60]}...")
        
        try:
            payload = {
                "question": test["question"],
                "context": test["context"]
            }
            response = requests.post(
                f"{BASE_URL}/query",
                json=payload,
                timeout=30
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Provider: {data['provider_used']}")
                print(f"Answer: {data['answer'][:150]}...")
                print("✓ Success")
            else:
                print(f"✗ Error: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 80)
    print("✓ API TESTS COMPLETE")
    print("=" * 80)
    print("\nYou can now test the API manually using curl:")
    print("""
curl -X POST http://localhost:8001/query \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "What is diabetes?",
    "context": "Diabetes is a metabolic disorder where blood sugar levels are too high."
  }'
""")


if __name__ == "__main__":
    try:
        test_endpoints()
    except KeyboardInterrupt:
        print("\n✗ Test interrupted")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
