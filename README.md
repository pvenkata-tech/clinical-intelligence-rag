# Clinical Intelligence RAG (Multi-Provider) 🏥 🤖

A production-grade Retrieval-Augmented Generation (RAG) pipeline designed for medical document intelligence. This system is architected with a **Model-Agnostic Provider Pattern**, allowing seamless switching between OpenAI, Anthropic, and AWS Bedrock without changing core business logic.

## 🚀 Key Features
- **Multi-LLM Support:** Native integration for **OpenAI (GPT-4o)**, **Anthropic (Claude 3.5)**, and **AWS Bedrock**.
- **Provider Factory:** A clean architectural pattern to switch models via environment variables for cost-optimization or compliance.
- **Enterprise RAG:** Hybrid search with Pinecone, document chunking with medical context awareness, and PHI masking hooks.
- **Async API:** High-performance endpoints built with **FastAPI** for real-time clinical querying.

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

## 🚦 Setup & Configuration
1. Clone: `git clone https://github.com/pvenkata-tech/clinical-intelligence-rag`
2. Environment: `cp .env.example .env`
3. **Switch Providers:** Simply change the `LLM_PROVIDER` variable in your `.env`:
   ```bash
   # Options: BEDROCK, OPENAI, ANTHROPIC
   LLM_PROVIDER=BEDROCK