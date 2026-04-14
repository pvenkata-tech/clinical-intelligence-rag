# Clean Architecture Refactoring - Project Structure Guide

## 📁 New Project Structure

```
clinical-intelligence-rag/
│
├── 🎯 Root Configuration Files
├── main.py                 # Entry point - imports from api/main.py
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (secrets)
├── .env.example            # Example config template
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
├── setup.sh                # Setup script
│
├── 🌐 api/                 # WEB LAYER - HTTP Interface
│   ├── __init__.py
│   ├── main.py             # FastAPI app factory & config
│   ├── routes.py           # Endpoint definitions (router)
│   └── schemas.py          # Pydantic models (Request/Response)
│
├── 🧠 core/                # AI ORCHESTRATION LAYER - Business Logic
│   ├── config.py           # Settings & environment loader
│   ├── ingestion.py        # Document parsing & processing
│   └── orchestrator.py     # RAG chain logic (The Brain)
│
├── 🤖 models/              # LLM PROVIDER LAYER - Model Abstraction
│   ├── factory.py          # Provider selector (OpenAI/Anthropic/Bedrock)
│   └── bedrock_client.py   # AWS Bedrock specific logic
│
├── ⚙️ services/             # INFRASTRUCTURE LAYER - Tools & Utilities
│   ├── __init__.py
│   ├── vector_db.py        # Pinecone integration
│   └── aws_service.py      # AWS credentials & session management
│
├── 💾 data/                # LOCAL DATA STORAGE (Gitignored - HIPAA safe)
│   ├── samples/            # Test PDFs for local development
│   ├── raw/                # Raw documents
│   └── processed/          # Processed embeddings & vectors
│
└── 🧪 tests/               # PRODUCTION-GRADE TEST SUITE
    ├── conftest.py         # Pytest fixtures & configuration
    ├── README.md           # Testing documentation
    ├── integration/        # Integration tests
    │   ├── test_providers.py
    │   ├── test_api_endpoints.py
    │   └── test_bedrock_integration.py
    └── unit/               # Unit tests (placeholder)
```

---

## 🏗️ Clean Architecture Layers Explained

### Layer 1: WEB LAYER (`api/`)
**Purpose:** HTTP interface and request/response handling
- **main.py**: FastAPI application factory
- **routes.py**: Endpoint handlers (GET /, POST /query)
- **schemas.py**: Pydantic models for validation

**Benefits:**
- Clean separation of concerns
- Easy to test endpoints in isolation
- Can easily swap FastAPI for another framework

---

### Layer 2: AI ORCHESTRATION LAYER (`core/`)
**Purpose:** Business logic and RAG orchestration
- **config.py**: Configuration management
- **orchestrator.py**: RAG chain logic (the "Brain")
- **ingestion.py**: Document processing pipeline

**Benefits:**
- Framework agnostic business logic
- Can be tested without HTTP concerns
- Easy to reuse in batch jobs or CLI

---

### Layer 3: LLM PROVIDER LAYER (`models/`)
**Purpose:** Abstract LLM provider implementations
- **factory.py**: Strategy pattern for provider selection
- **bedrock_client.py**: AWS-specific implementations

**Benefits:**
- Easy to swap providers (OpenAI ↔ Anthropic ↔ Bedrock)
- Vendor-specific logic isolated
- Testable with mocks

---

### Layer 4: INFRASTRUCTURE LAYER (`services/`)
**Purpose:** Tools, integrations, and external services
- **vector_db.py**: Pinecone vector database client
- **aws_service.py**: AWS credentials & session management

**Benefits:**
- Centralized credential management
- Easy to mock in tests
- Reusable across components
- Singleton pattern prevents connection leaks

---

### Layer 5: DATA LAYER (`data/`)
**Purpose:** Local storage for PDFs and embeddings
- **samples/**: Test PDFs for development
- **raw/**: Raw medical documents
- **processed/**: Embeddings and vectors

**⚠️ SECURITY:** This entire folder is `.gitignored` to prevent accidental commits of sensitive HIPAA data.

---

### Layer 6: TEST LAYER (`tests/`)
**Purpose:** Comprehensive test coverage
- **Integration tests**: Test component interactions
- **Unit tests**: Test individual functions
- **Fixtures**: Shared test data and configuration

---

## 🔄 Dependency Flow (Correct Direction)

```
OUTER LAYERS (High-level)
        ↓
    api/ (routes → schemas)
        ↓
    core/ (orchestrator)
        ↓
    models/ (factory)
        ↓
    services/ (tools)
        ↓
INNER LAYERS (Low-level)
```

**Key Rule:** Inner layers should NEVER import from outer layers.
- ❌ `core/orchestrator.py` should NOT import from `api/routes.py`
- ✅ `api/routes.py` CAN import from `core/orchestrator.py`

---

## 🚀 Running the Application

### Start with Default Provider (OpenAI)
```bash
python main.py
# Runs on http://0.0.0.0:8000
```

### Start with Specific Provider
```bash
# Anthropic
LLM_PROVIDER=ANTHROPIC python main.py

# Bedrock (with AWS credentials)
LLM_PROVIDER=BEDROCK python main.py

# Custom port
API_PORT=8001 python main.py
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=core --cov=models --cov=services
```

---

## 📊 Architecture Benefits

| Aspect | Benefit |
|--------|---------|
| **Testability** | Each layer can be tested independently |
| **Maintainability** | Clear separation of concerns |
| **Scalability** | Easy to add new providers or services |
| **Reusability** | Core logic can be used in batch/CLI jobs |
| **Portability** | Business logic is framework-agnostic |
| **Security** | Sensitive data in data/ is .gitignored |

---

## 🔗 Inter-Layer Communication

### API Layer → Core Layer
```python
# api/routes.py
from core.orchestrator import ClinicalRAGOrchestrator
orchestrator = ClinicalRAGOrchestrator()
answer = orchestrator.query(question, context)
```

### Core Layer → Models Layer
```python
# core/orchestrator.py
from models.factory import ModelFactory
model = ModelFactory.get_model()
```

### Models Layer → Services Layer
```python
# models/bedrock_client.py
from services.aws_service import AWSService
aws = AWSService()
client = aws.bedrock_client
```

---

## 📝 Migration Checklist

- ✅ Created `api/` with main.py, routes.py, schemas.py
- ✅ Root main.py updated to import from api/main.py
- ✅ Created `services/` with vector_db.py, aws_service.py
- ✅ Created `data/samples/` directory structure
- ✅ Updated .gitignore for HIPAA safety
- ✅ core/, models/ remain unchanged (no impact on existing logic)
- ✅ tests/ directory already in place
- ✅ All imports follow dependency direction

---

## 🎯 Next Steps

1. **Add unit tests** in `tests/unit/` for isolated component testing
2. **Implement vector DB** in `services/vector_db.py` when Pinecone is ready
3. **Add logging** across all layers for debugging
4. **Add middleware** in `api/main.py` for request/response logging
5. **Consider API versioning** (api/v1/, api/v2/) for future compatibility

---

## 📚 References

- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [FastAPI Project Structure](https://fastapi.tiangolo.com/)
- [HIPAA Compliance & Gitignore](https://www.hipaa.gov/)

