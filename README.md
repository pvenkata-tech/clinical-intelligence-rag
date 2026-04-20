# Clinical Intelligence RAG 🏥 🤖

[![Overall: 0.99](https://img.shields.io/badge/Overall-0.99-brightgreen)](eval_results.json) [![Faithfulness: 1.00](https://img.shields.io/badge/Faithfulness-1.00-brightgreen)](eval_results.json) [![Precision: 1.00](https://img.shields.io/badge/Precision-1.00-brightgreen)](eval_results.json)

A privacy-first RAG pipeline designed for healthcare, implementing PII scrubbing and AWS Bedrock integration to ensure HIPAA-compliant AI inference.

## Quick Start

```bash
docker-compose up --build
# API:  http://localhost:8000/docs
# UI:   http://localhost:8501
```

### Project Architecture

```mermaid
graph TD
    A["📄 Clinical PDFs"] --> B["🛠️ Ingestion<br/>(Parse & Chunk)"]
    B -->|PHI Scrubbing| C["🧬 Embeddings<br/>(Multi-Provider)"]
    C --> D[("🌲 Pinecone<br/>Vector DB")]
    
    subgraph RAG["⚙️ RAG Engine"]
    D <-->|Semantic Search| E["🔍 Retrieval<br/>& Compression"]
    E -->|Relevant Context| F["🏭 LLM Provider<br/>Selection"]
    F -->|OpenAI/Anthropic/Bedrock| G["🧠 Generate<br/>Answer"]
    end
    
    G -->|Grounded Response| H["🚀 FastAPI<br/>REST API"]
    
    subgraph UI["👥 User Interface Layer"]
    H --> I["💻 Streamlit<br/>Dashboard"]
    I --> J["🏥 Clinical<br/>Intelligence"]
    end
    
    style A fill:#e8f5e9
    style D fill:#1b5e20,stroke:#fff,color:#fff,stroke-width:3px
    style G fill:#4a148c,stroke:#fff,color:#fff,stroke-width:3px
    style RAG fill:#f5f5f5,stroke:#666,stroke-width:2px
    style UI fill:#fff3e0,stroke:#ff6f00,stroke-width:2px
    style H fill:#ff9800,stroke:#fff,color:#fff,stroke-width:2px
    style I fill:#ffb74d,stroke:#fff,color:#333,stroke-width:2px
    style J fill:#0d2949,stroke:#fff,color:#fff,stroke-width:3px
```

## Features

- 📄 Upload PDFs  
- 💬 Ask questions → AI answers from docs  
- 📥 Export analysis  
- 🔐 De-identify PHI (HIPAA)  
- ⚡ 20-30% fewer tokens (compression)  
- 🔄 Any LLM (swap in `.env`)  
- ✅ Validated (F:1.00, P:1.00)  
- 📊 Production Monitoring** (LangSmith tracing)

## Quality

| Metric | Score |
|--------|-------|
| Faithfulness | 1.00 |
| Relevancy | 0.97 |
| Precision | 1.00 |
| **Overall** | **0.99** |

## Docs

- [SETUP.md](docs/SETUP.md) - Install
- [API.md](docs/API.md) - REST API
- [UI.md](docs/UI.md) - Dashboard
- [FEATURES.md](docs/FEATURES.md) - Advanced
- [MONITORING.md](docs/MONITORING.md) - 📊 LangSmith Tracing
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Help
- [DOCKER.md](docs/DOCKER.md) - Deploy
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Design

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend API** | FastAPI | REST endpoints, async request handling |
| **Frontend UI** | Streamlit | Interactive dashboard, document upload |
| **LLM Orchestration** | LangChain | Chain-of-thought reasoning, prompt management |
| **Vector Database** | Pinecone | Semantic search, embeddings storage |
| **Evaluation** | Ragas Framework | RAG quality metrics (Faithfulness, Precision, Recall) |
| **Containerization** | Docker + Compose | Production deployment, multi-service orchestration |
| **LLM Providers** | OpenAI, Anthropic, AWS Bedrock | Multi-provider support (plug-and-play) |
| **Embeddings** | OpenAI/Anthropic/Bedrock | Text-to-vector conversion |
| **Testing** | Pytest | Unit + integration tests |
| **Language** | Python 3.11+ | Core implementation language |
| **Monitoring** | LangChain Tracing (LangSmith) | Debug RAG pipeline, token tracking, latency analysis |

## What's Inside

✅ Provider Factory (swap LLMs)  
✅ Contextual Compression (20-30% tokens)  
✅ PHI De-identification (HIPAA)  
✅ Gold QA Benchmarks  
✅ Ragas Evaluation  
✅ LangSmith Monitoring** (production observability)  

## Help

[SETUP.md](docs/SETUP.md) • [API.md](docs/API.md) • [MONITORING.md](docs/MONITORING.md) • [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Evaluation

**Run Evaluation:**
```bash
python eval/evaluate_rag.py
```

**Expected Results:**
- Faithfulness: 1.00/1.00
- Answer Relevancy: 0.97/1.00
- Context Precision: 1.00/1.00
- Overall Score: 0.99/1.00

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

---

## 🔍 Optional: Enable LangChain Tracing (LangSmith)

For debugging and monitoring RAG pipeline execution, you can enable **LangChain tracing** via [LangSmith](https://smith.langchain.com):

1. **Sign up for LangSmith** (free tier available)
2. **Get your API key** from LangSmith dashboard
3. **Add to your `.env`:**
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-langsmith-api-key
   ```

4. **Run your queries** - traces will automatically be sent to LangSmith:
   ```bash
   python test_query.py
   ```

The system will print: `🔍 LangChain tracing enabled - traces will be sent to LangSmith`

**Benefits:**
- Monitor token usage and latency
- Debug RAG chain execution step-by-step
- Track LLM calls, embeddings, and retrieved context
- Visualize the complete prompt flow
