# FastAPI Backend Documentation 🔌

Complete guide to using the Clinical Intelligence RAG REST API.

## Starting the API Server

```bash
python main.py
```

The API will run on **http://0.0.0.0:8000**

## Interactive API Documentation

Once the server is running, visit **http://localhost:8000/docs** to access the interactive Swagger UI where you can test all endpoints directly.

## Available Endpoints

### Health Check
```bash
GET /
```

Simple health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Submit Clinical Query
```bash
POST /query
```

Submit a clinical question and receive AI-powered responses using the RAG pipeline.

**Request Body:**
```json
{
  "question": "What is the patient's oxygen saturation and the doctor's plan?"
}
```

**Response:**
```json
{
  "question": "What is the patient's oxygen saturation and the doctor's plan?",
  "answer": "The patient's oxygen saturation is 98% on room air. The doctor's plan is to monitor oxygen levels during activity and provide supplemental oxygen if saturation drops below 95%.",
  "context_sources": [
    {
      "source": "document_name.pdf",
      "page": 2,
      "relevance_score": 0.98
    }
  ]
}
```

## Usage Examples

### Python Client
```python
import requests

api_url = "http://localhost:8000/query"
payload = {
    "question": "What medications is the patient taking?"
}

response = requests.post(api_url, json=payload)
result = response.json()
print(result["answer"])
```

### cURL Command
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the patient'\''s current diagnosis?"
  }' \
  | jq .
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "What is the patient's oxygen saturation?"
  })
});

const data = await response.json();
console.log(data.answer);
```

## How It Works

The RAG pipeline processes your query as follows:

1. **Semantic Search** - Your question is embedded and compared against the Pinecone vector database
2. **Context Retrieval** - The top 4 most relevant clinical document chunks are retrieved
3. **Contextual Compression** - Retrieved chunks are re-ranked and noisy segments filtered
4. **LLM Processing** - The question + context are sent to your selected LLM provider
5. **Response Generation** - The LLM generates a clinical response grounded in the retrieved context

## Configuring LLM Providers

The API automatically uses the LLM provider specified in your `.env` file:

```bash
LLM_PROVIDER=ANTHROPIC  # Default to Claude 3.5 Sonnet
LLM_PROVIDER=OPENAI     # Use GPT-4o
LLM_PROVIDER=BEDROCK    # Use AWS Bedrock (Claude Sonnet)
```

### Cost Optimization Tips

- **For extraction tasks:** Use OpenAI's GPT-4o-mini (cheapest)
- **For complex reasoning:** Use Claude 3.5 Sonnet (best quality)
- **For HIPAA compliance:** Use AWS Bedrock (compliant deployment)

## Performance Tuning

### Adjust Retrieval Parameters

Modify the number of context chunks retrieved:

```python
# In core/orchestrator.py
docs = vdb.similarity_search(prompt, k=3)  # Lower k = faster, less context
docs = vdb.similarity_search(prompt, k=10) # Higher k = slower, more context
```

### Enable/Disable Contextual Compression

```python
# Enable compression (default)
docs = vdb.similarity_search(prompt, enable_compression=True)

# Disable for testing
docs = vdb.similarity_search(prompt, enable_compression=False)
```

## Error Handling

### Common API Errors

**400 Bad Request:**
```json
{
  "detail": "Missing required field: 'question'"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to connect to Pinecone vector database"
}
```

Check your `.env` configuration and API keys if you encounter errors.

## Deployment

For production deployment with Docker:

```bash
docker-compose up --build
```

See [DOCKER.md](DOCKER.md) for detailed containerization instructions.

## Monitoring & Debugging

Enable LangChain tracing for detailed pipeline monitoring:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-key
python main.py
```

Traces will be sent to [LangSmith](https://smith.langchain.com) for analysis.

## Next Steps

- **UI Usage:** See [UI.md](UI.md)
- **Advanced Features:** See [FEATURES.md](FEATURES.md)
- **Setup Guide:** See [SETUP.md](SETUP.md)
