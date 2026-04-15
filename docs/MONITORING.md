# LangSmith Monitoring Guide 📊

Transform your Clinical RAG from a "leisure project" to a "reliability project" with production-grade observability.

## Quick Start (2 minutes)

### 1. Enable LangSmith Tracing

**Create Account:**
- Go to [smith.langchain.com](https://smith.langchain.com)
- Sign up (free tier)
- Get API key from dashboard

**Update `.env`:**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
```

**Restart System:**
```bash
docker-compose down
docker-compose up --build
```

**That's it!** Every RAG query is now traced automatically.

---

## What You Get 🎯

### Local Monitoring Dashboard
- **Access:** http://localhost:8501 → "📊 Monitoring" sidebar
- **Shows:**
  - Real-time query latency trends
  - Provider performance comparison
  - Recent query history with metrics
  - Error tracking
  - Query details (question, answer, metrics)

### LangSmith Dashboard
- **Access:** https://smith.langchain.com
- **Shows:**
  - Every LLM call (prompt, completion, tokens)
  - Every embedding call (tokens, latency)
  - Full chain execution flow
  - Token costs and latency breakdown
  - Error traces with stack traces
  - Dataset management for evaluation
  - Feedback collection for quality improvement

### REST API Endpoints
```bash
# Get summary stats
curl http://localhost:8000/monitoring/stats

# Get recent queries
curl "http://localhost:8000/monitoring/queries?limit=10"

# Compare providers
curl http://localhost:8000/monitoring/providers

# Check status
curl http://localhost:8000/monitoring/status
```

---

## Architecture 🏗️

```
Clinical RAG Query
    ↓
ClinicalRAGOrchestrator.query() [captures metrics]
    ├─ Latency (ms)
    ├─ Token count
    ├─ Retrieved chunks
    ├─ Provider used
    └─ Errors
    ↓
MonitoringService [stores & aggregates]
    ├─ In-memory history (500 max queries)
    ├─ API endpoints
    └─ LangSmith integration (automatic via env vars)
    ↓
Two Dashboards
    ├─ Local: Streamlit
    │  └─ Real-time metrics, trends, recent queries
    └─ LangSmith: https://smith.langchain.com
       └─ Chain execution, tokens, costs, debugging
```

---

## Key Metrics Explained 📈

### Performance Metrics

**Latency (ms)**
- Time from question to answer
- Includes: retrieval + compression + LLM inference
- Goal: < 3000ms for interactive use

**Token Count**
- Total tokens per query (question + context + answer)
- Goal: < 2000 for cost efficiency

**Retrieved Chunks**
- Number of context segments from vector DB
- Goal: 3-5 for balanced accuracy

**Error Rate**
- Percentage of failed queries
- Goal: < 1%

### Provider Comparison

Compare OpenAI, Anthropic, and AWS Bedrock:
- Average latency per query
- Token usage
- Error rates
- Query count

---

## Debugging Scenarios 🔧

### Scenario: High Latency

1. **Check Dashboard:**
   - Latency Trend → identify when it spiked
   - Provider Performance → which provider is slow?

2. **Check LangSmith:**
   - View specific trace: https://smith.langchain.com
   - See where time is spent (retrieval vs LLM vs embedding)

3. **Common Causes:**
   - Vector search slow → scale Pinecone index
   - LLM slow → check provider rate limits or model
   - Network latency → check region

### Scenario: High Token Usage

1. **Check Dashboard:**
   - See avg tokens per provider
   - Identify which queries use most tokens

2. **Check LangSmith:**
   - See exact prompts and responses
   - Identify inefficient prompts

3. **Solutions:**
   - Enable `ENABLE_COMPRESSION=true` (saves 20-30%)
   - Shorten context window
   - Use cheaper model (Anthropic Claude vs GPT-4)

### Scenario: Errors

1. **Check Dashboard:**
   - Recent Queries → Error Rate
   - Click failed query to see error message

2. **Check LangSmith:**
   - See full stack trace
   - Check LLM response and context

3. **Common Causes:**
   - API key invalid
   - Rate limits exceeded
   - Model not available in region
   - Invalid prompt format

---

## Example: Setting Up for Production 🚀

### Step 1: Create LangSmith Account & Project
```bash
# Go to https://smith.langchain.com
# Create account → Create project → Get API key
```

### Step 2: Enable Tracing in Docker
```yaml
# docker-compose.yml
services:
  api:
    environment:
      - LANGCHAIN_TRACING_V2=true
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
  
  ui:
    environment:
      - LANGCHAIN_TRACING_V2=true
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
```

### Step 3: Deploy
```bash
export LANGCHAIN_API_KEY=your-key
docker-compose up --build
```

### Step 4: Monitor
- **Local:** http://localhost:8501 (Streamlit Dashboard)
- **Remote:** https://smith.langchain.com (LangSmith)

---

## Cost Tracking 💰

LangSmith shows:
- Free tier: 1000 traces/month
- Cost per trace: $0.03 (paid tier)
- Easy to estimate monthly costs

**Cost Optimization:**
- Use contextual compression (-20% tokens)
- Use cheaper model (Claude vs GPT-4)
- Batch queries when possible
- Monitor token usage regularly

---

## Best Practices ✅

1. **Always enable LangSmith in production** ← immediate ROI
2. **Check metrics weekly** → spot issues early
3. **Compare providers quarterly** → optimize costs
4. **Set up alerts** → notify if error rate > 5%
5. **Export metrics monthly** → track trends

---

## REST API Reference 🔌

### GET /monitoring/stats
```json
{
  "total_queries": 150,
  "successful_queries": 148,
  "avg_latency_ms": 2456.7,
  "error_rate": 1.33,
  "providers": {
    "OPENAI": {
      "count": 75,
      "avg_latency": 2100
    }
  }
}
```

### GET /monitoring/queries?limit=10
```json
{
  "queries": [
    {
      "query_id": "uuid",
      "timestamp": "2026-04-14T...",
      "question": "What was the patient's diagnosis?",
      "answer": "Based on the records...",
      "provider": "OPENAI",
      "latency_ms": 2345.6,
      "token_count": 1850,
      "retrieved_chunks": 3,
      "error": null
    }
  ],
  "total_tracked": 150
}
```

### GET /monitoring/providers
```json
{
  "OPENAI": {
    "queries": 75,
    "avg_latency": 2100,
    "avg_tokens": 1850,
    "error_rate": 1.33
  },
  "ANTHROPIC": {
    "queries": 50,
    "avg_latency": 2300,
    "avg_tokens": 1700,
    "error_rate": 0.0
  }
}
```

### GET /monitoring/status
```json
{
  "status": "operational",
  "langsmith_enabled": true,
  "queries_tracked": 150,
  "langsmith_dashboard": "https://smith.langchain.com"
}
```

---

## Troubleshooting 🛠️

### LangSmith not capturing traces

✅ **Check environment variables:**
```bash
echo $LANGCHAIN_TRACING_V2  # Should be 'true'
echo $LANGCHAIN_API_KEY      # Should not be empty
```

✅ **Check LangSmith dashboard:**
- Go to https://smith.langchain.com
- Check Project Settings
- Verify API key is correct

✅ **Restart containers:**
```bash
docker-compose down
docker-compose up --build
```

### Dashboard showing no queries

✅ **Make sure you ran a query:**
- Use the Chat interface
- Run: `python test_query.py`

✅ **Check API is running:**
```bash
curl http://localhost:8000/monitoring/status
```

✅ **Check logs:**
```bash
docker logs clinical-intelligence-rag-api-1
```

---

## Next Steps 🎯

- [ ] Enable LangSmith (this guide)
- [ ] Run a few queries and check that traces appear
- [ ] Explore LangSmith dashboard features
- [ ] Set up alerts via LangSmith notifications
- [ ] Review metrics weekly

---

## Resources 📚

- **LangSmith Docs:** https://docs.smith.langchain.com
- **LangChain Docs:** https://python.langchain.com
- **Observability Guide:** https://docs.smith.langchain.com/concepts/tracing

---

*Last Updated: April 2026*
