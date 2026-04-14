# Clinical Intelligence RAG (Multi-Provider) 🏥 🤖

A production-grade Retrieval-Augmented Generation (RAG) pipeline designed for medical document intelligence. This system is architected with a **Model-Agnostic Provider Pattern**, allowing seamless switching between OpenAI, Anthropic, and AWS Bedrock without changing core business logic.

## 🚀 Key Features
- **Multi-LLM Support:** Native integration for **OpenAI (GPT-4o)**, **Anthropic (Claude 3.5)**, and **AWS Bedrock**.
- **Provider Factory:** A clean architectural pattern to switch models via environment variables for cost-optimization or compliance.
- **Enterprise RAG:** Hybrid search with Pinecone, document chunking with medical context awareness, and PHI masking hooks.
- **Async API:** High-performance endpoints built with **FastAPI** for real-time clinical querying.

## 📁 Project Architecture
For detailed information on the clean architecture design, project structure, layers, and design patterns used in this project, please refer to the comprehensive documentation in [ARCHITECTURE.md](ARCHITECTURE.md).

Key architectural highlights:
- **Clean Layered Architecture:** API → Core → Models → Services
- **Provider Factory Pattern:** Vendor-agnostic LLM switching
- **HIPAA Compliance:** Sensitive data isolation with `.gitignore` protection

### RAG Data Flow
```
Clinical PDF (data/samples/)
        ↓
   Ingestion Layer (PyPDF, LangChain)
        ↓
   Chunking & Embedding (Pinecone + Bedrock/OpenAI)
        ↓
   Vector Database (Pinecone)
        ↓
   Semantic Search (K-NN Retrieval)
        ↓
   Context + Question → LLM (OpenAI/Anthropic/Bedrock)
        ↓
   Clinical Response (FastAPI → JSON)
```

## 🏗️ Architectural Pattern: The Provider Factory
The project uses an abstract base class strategy to ensure that the orchestration logic remains decoupled from the specific LLM implementation. This prevents **Model Lock-In** and allows for:
1. **Compliance Routing:** Use Bedrock for HIPAA-sensitive data.
2. **Cost Routing:** Use GPT-4o-mini for simple extraction tasks.
3. **Performance Routing:** Use Claude 3.5 Sonnet for complex clinical reasoning.

## 🛠️ Tech Stack
- **Frameworks:** LangChain, LangGraph
- **Providers:** AWS Bedrock, OpenAI, Anthropic
- **Vector DB:** Pinecone
- **Infrastructure:** Python 3.11+, Docker, Boto3
- **API:** FastAPI + Uvicorn
- **Testing:** pytest

## 📋 Prerequisites
Before you begin, ensure you have:
- **Python 3.11+** installed
- **pip** or **conda** for package management
- **API Keys** for at least one LLM provider:
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic: https://console.anthropic.com
  - AWS Bedrock: Requires AWS account with Bedrock enabled
- **Pinecone Account** for vector database: https://app.pinecone.io
- Virtual environment setup (recommended)

## � Quickstart
1. Clone and run `bash setup.sh`
2. Add your keys to `.env`
3. Drop your clinical PDFs into `data/samples/`
4. Run `python sync_data.py` to index the data
5. Run `python test_query.py` to see the RAG in action

## 🛠️ Setup & Configuration

### 1. Clone the Repository
```bash
git clone https://github.com/pvenkata-tech/clinical-intelligence-rag
cd clinical-intelligence-rag
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# --- LLM Provider Selection ---
# Options: BEDROCK, OPENAI, ANTHROPIC
LLM_PROVIDER=ANTHROPIC

# --- OpenAI Configuration ---
OPENAI_API_KEY=sk-your-openai-key-here

# --- Anthropic Configuration ---
ANTHROPIC_API_KEY=your-anthropic-key-here

# --- AWS Bedrock Configuration ---
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

# --- Vector Database (Pinecone) ---
PINECONE_API_KEY=your-pinecone-key-here
PINECONE_INDEX_NAME=clinical-rag
```

**Note for AWS Users:** Ensure you have requested access to the Claude 4.x models in your AWS Bedrock console. The system defaults to `anthropic.claude-4-6-sonnet-20260217-v1:0`. If this model is unavailable, the system will gracefully fall back to Anthropic or OpenAI.

### 5. Switch LLM Providers
To use a different provider, simply change the `LLM_PROVIDER` variable:
```bash
# Using Bedrock
LLM_PROVIDER=BEDROCK python main.py

# Using OpenAI
LLM_PROVIDER=OPENAI python test_query.py

# Using Anthropic (default)
LLM_PROVIDER=ANTHROPIC python test_query.py
```

---

## 🔌 Running the FastAPI Server
Start the REST API server for production use:
```bash
python main.py
```
The API will run on `http://0.0.0.0:8000`

📝 **Interactive Documentation:** Once the server is running, visit [http://localhost:8000/docs](http://localhost:8000/docs) to access the interactive Swagger UI where you can test all endpoints directly.

**Available endpoints:**
- `GET /` - Health check
- `POST /query` - Submit a clinical query (RAG-based, retrieves context automatically from Pinecone)
  ```bash
  curl -X POST http://localhost:8000/query \
    -H "Content-Type: application/json" \
    -d '{
      "question": "What is the patient'\''s oxygen saturation and the doctor'\''s plan?"
    }'
  ```
  The system will automatically:
  1. Search Pinecone for relevant clinical context
  2. Pass the context + question to the selected LLM
  3. Return a clinical response

---

## 🩺 Troubleshooting

**ValidationException (Bedrock):** Ensure your AWS region supports the selected model and that you have active model access in your Bedrock console.

**IndexNotFound (Pinecone):** Ensure the `PINECONE_INDEX_NAME` in your `.env` matches the index you created in the Pinecone dashboard.

**ModuleNotFoundError:** Ensure you have activated your virtual environment:
```bash
# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/Mac:
source .venv/bin/activate
```

**No working Bedrock models found:** This is expected if you don't have an AWS account or Bedrock access. The system automatically falls back to Anthropic (Claude 3.5 Sonnet) or OpenAI (GPT-4o) as configured in your `.env`.