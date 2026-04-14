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
