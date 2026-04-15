# Setup & Configuration Guide 🛠️

Complete step-by-step instructions for setting up the Clinical Intelligence RAG system.

## Prerequisites

Before you begin, ensure you have:
- **Python 3.11+** installed
- **pip** or **conda** for package management
- **API Keys** for at least one LLM provider:
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic: https://console.anthropic.com
  - AWS Bedrock: Requires AWS account with Bedrock enabled
- **Pinecone Account** for vector database: https://app.pinecone.io
- Virtual environment setup (recommended)

## Installation Steps

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

Copy the example environment file:
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

## AWS Bedrock Setup Notes

⚠️ **Important:** Ensure you have requested access to the Claude 4.x models in your AWS Bedrock console.

The system defaults to `anthropic.claude-4-6-sonnet-20260217-v1:0`. If this model is unavailable, the system will gracefully fall back to Anthropic or OpenAI based on your `.env` configuration.

## Docker Setup

For one-command installation with Docker:

```bash
docker-compose up --build
```

See [DOCKER.md](DOCKER.md) for comprehensive Docker deployment guide.

## Verification

Test your setup:

```bash
# Test basic imports
python -c "from core.orchestrator import ClinicalRAGOrchestrator; print('✅ Setup successful')"

# Run a test query
python test_query.py

# Start the API
python main.py

# In another terminal, start the UI
streamlit run ui/app.py
```

## Next Steps

- **API Development:** See [API.md](API.md)
- **UI Usage:** See [UI.md](UI.md)
- **Advanced Features:** See [FEATURES.md](FEATURES.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
