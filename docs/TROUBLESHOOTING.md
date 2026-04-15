# Troubleshooting Guide 🩺

Common issues and solutions for the Clinical Intelligence RAG system.

## Installation & Setup Issues

### ModuleNotFoundError

**Error:** `ModuleNotFoundError: No module named 'core'`

**Causes:**
- Virtual environment not activated
- PYTHONPATH not set correctly
- Dependencies not installed

**Solutions:**

```bash
# 1. Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1

# Linux/Mac:
source .venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Or set PYTHONPATH explicitly
export PYTHONPATH=.
python test_query.py
```

---

### Import Errors with Streamlit

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit>=1.28.0
pip install -r requirements.txt
```

---

## Configuration & Environment

### Missing API Keys

**Error:** `KeyError: 'OPENAI_API_KEY'` or similar

**Causes:**
- `.env` file not created
- API key not in `.env`
- `.env` has typos in variable names

**Solutions:**

```bash
# 1. Create .env from example
cp .env.example .env

# 2. Verify contents
cat .env

# 3. Check for typos in variable names
# Should be exactly: OPENAI_API_KEY (not OPENAI_KEY)

# 4. Reload credentials
source .env  # Linux/Mac
# or
set-content -path .env -encoding utf8  # PowerShell
```

---

### AWS Bedrock Connection Issues

**Error:** `ValidationException: The model specified in the request is not found`

**Causes:**
- Model not available in your AWS region
- Model access not requested in Bedrock console
- Incorrect AWS credentials

**Solutions:**

```bash
# 1. Verify AWS credentials are correct
aws sts get-caller-identity

# 2. Check Bedrock model availability
aws bedrock list-foundation-models --region us-east-1

# 3. Request model access in AWS Console:
# - Go to AWS Bedrock console
# - Click "Model access"
# - Request access to Claude 3.5 Sonnet
# - Wait 1-5 minutes for approval

# 4. Verify in .env
cat .env | grep AWS_REGION
# Should match where models are available (us-east-1, us-west-2, etc.)
```

---

### Pinecone Connection Issues

**Error:** `ConnectionError: Failed to connect to Pinecone` or `IndexNotFound`

**Causes:**
- Pinecone API key invalid or expired
- Index doesn't exist in Pinecone
- Index name typo in `.env`
- Network connectivity issue

**Solutions:**

```bash
# 1. Verify Pinecone API key
echo $PINECONE_API_KEY  # Should print your key

# 2. Check index exists in Pinecone dashboard
# https://app.pinecone.io
# - Navigate to "Indexes"
# - Verify your index name matches .env exactly

# 3. Verify .env spelling
grep PINECONE_INDEX_NAME .env
# Should exactly match: clinical-rag (or your custom name)

# 4. Test connection
python -c "from services.vector_db import VectorStoreManager; vdb = VectorStoreManager(); print('✅ Connected')"
```

---

## Runtime Issues

### No Documents Indexed Error

**Error:** `No documents found in vector database` or empty results

**Causes:**
- No documents uploaded to the system
- Documents uploaded but indexing failed
- Wrong Pinecone index selected

**Solutions:**

```bash
# 1. Upload documents via Streamlit UI
# - Open http://localhost:8501
# - Upload PDF in sidebar
# - Click "Process & Index Document"

# 2. Or upload via API
python sync_data.py

# 3. Verify documents are indexed
python -c "
from services.vector_db import VectorStoreManager
vdb = VectorStoreManager()
docs = vdb.similarity_search('test', k=1)
print(f'Documents indexed: {len(docs)}')
"

# 4. Check document location
ls -la data/samples/  # Should contain PDFs
```

---

### Slow Performance / Timeout

**Error:** `Request timeout` or API takes >30 seconds to respond

**Causes:**
- Large documents being processed
- Pinecone index overloaded
- Network latency issues
- Compression disabled (comparing all chunks)

**Solutions:**

```bash
# 1. Optimize retrieval parameters in core/orchestrator.py
docs = vdb.similarity_search(prompt, k=3)  # Reduce from default k=4

# 2. Enable contextual compression
docs = vdb.similarity_search(prompt, enable_compression=True)

# 3. Use faster LLM provider
LLM_PROVIDER=OPENAI python main.py  # Faster than Anthropic/Bedrock

# 4. Check Pinecone index stats
# In Pinecone dashboard: Check query latency and vector count

# 5. Monitor local resources
# Check CPU/memory aren't maxed out
# Kill other processes consuming resources
```

---

### Memory Issues

**Error:** `MemoryError` or `Out of memory`

**Causes:**
- Processing very large PDFs (>100MB)
- Too many documents loaded at once
- Insufficient system RAM

**Solutions:**

```bash
# 1. Process documents in batches
# Process one PDF at a time via Streamlit

# 2. Split large PDFs before uploading
# Use PDF splitting tool: https://smallpdf.com/split-pdf

# 3. Increase virtual memory (temporary)
# Linux:
# fallocate -l 4G /swapfile
# chmod 600 /swapfile
# mkswap /swapfile
# swapon /swapfile

# 4. Monitor memory usage
# Linux: watch -n 1 free -h
# Mac: vm_stat
```

---

## API Issues

### CORS Errors

**Error:** `No 'Access-Control-Allow-Origin' header`

**Causes:**
- Frontend on different domain than API
- CORS not configured in FastAPI

**Solution:**

In `api/main.py`, the CORS middleware is already configured:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

No changes needed unless you want to restrict origins for security.

---

### Invalid JSON Response

**Error:** `JSONDecodeError` or garbled response

**Causes:**
- LLM response formatting issue
- Encoding mismatch
- API endpoint returning non-JSON

**Solution:**

```bash
# Test endpoint directly
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' \
  | python -m json.tool  # Pretty print JSON
```

---

## Docker Issues

### Container Won't Start

**Error:** `docker-compose: command not found` or container exits immediately

**Causes:**
- Docker/Docker Compose not installed
- Port already in use (8000 or 8501)
- Environment variables not passed

**Solutions:**

```bash
# 1. Check Docker installation
docker --version
docker-compose --version

# 2. Kill processes on ports
# Linux/Mac:
lsof -i :8000  # Find process on port 8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 3. Rebuild containers
docker-compose down -v
docker-compose up --build

# 4. Check logs
docker-compose logs -f api
docker-compose logs -f ui
```

---

## LLM Provider Issues

### OpenAI Rate Limiting

**Error:** `RateLimitError: Rate limit exceeded`

**Solution:**
```bash
# Switch to different provider temporarily
LLM_PROVIDER=ANTHROPIC python main.py

# Or wait 60 seconds before retrying
```

---

### Anthropic Connection Issues

**Error:** `APIError: Connection refused`

**Causes:**
- Invalid API key
- Network blocking Anthropic API
- Region restrictions

**Solution:**
```bash
# Verify API key
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: your-key-here"

# Use OpenAI or Bedrock as fallback
LLM_PROVIDER=OPENAI python main.py
```

---

### Bedrock Model Errors

**Error:** `InvalidModelIdException` or `AccessDeniedException`

**Causes:**
- Model ID incorrect
- Model access not enabled
- Wrong AWS region

**Solution:**
```bash
# List available models
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query 'modelSummaries[].modelId'

# Update core/config.py with correct model ID
# Then update BEDROCK_MODEL_ID in .env
```

---

## Getting Help

If you still need help after trying these solutions:

1. **Check logs in detail:**
   ```bash
   # Full application logs
   python main.py 2>&1 | tee debug.log
   streamlit run ui/app.py 2>&1 | tee ui.log
   ```

2. **Check GitHub Issues:** https://github.com/pvenkata-tech/clinical-intelligence-rag/issues

3. **Enable debug mode:**
   ```bash
   export DEBUG=1
   export LANGCHAIN_DEBUG=true
   python main.py
   ```

4. **Collect system info:**
   ```bash
   python --version
   pip freeze | grep -E "langchain|openai|anthropic|boto3"
   docker --version
   ```

5. **Review documentation:**
   - [SETUP.md](SETUP.md) - Installation & configuration
   - [API.md](API.md) - API endpoints
   - [UI.md](UI.md) - Streamlit dashboard
   - [FEATURES.md](FEATURES.md) - Advanced features
