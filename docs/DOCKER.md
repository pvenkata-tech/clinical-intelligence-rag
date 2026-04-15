# Docker Deployment Guide 🐳

This guide explains how to deploy the **Clinical Intelligence RAG** system using Docker and Docker Compose.

## Quick Start

### Prerequisites
- Docker (v20.10+)
- Docker Compose (v1.29+)
- `.env` file configured with your API keys

### One-Command Deploy

```bash
# Build and start both services (API + UI)
docker-compose up --build

# In another terminal, verify services are running
docker ps
```

Your services will be available at:
- **API (FastAPI):** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **UI (Streamlit):** http://localhost:8501

---

## Service Architecture

### 1. **API Service** (FastAPI Backend)
```yaml
Container: clinical-rag-api
Port: 8000
Command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Responsibilities:**
- REST API endpoints for clinical queries
- RAG pipeline orchestration
- Vector database integration
- LLM provider abstraction

**Health Check:** `GET /` endpoint polls every 30 seconds

**Access Swagger UI:** http://localhost:8000/docs

### 2. **UI Service** (Streamlit Dashboard)
```yaml
Container: clinical-rag-ui
Port: 8501
Command: streamlit run ui/app.py --server.port=8501 --server.address=0.0.0.0
```

**Responsibilities:**
- Interactive clinical dashboard
- Document upload and ingestion
- Chat interface for queries
- Clinical analysis export

**Health Check:** `GET /` endpoint polls every 30 seconds

**Access Dashboard:** http://localhost:8501

---

## Environment Configuration

### Create `.env` file in project root:

```bash
# Copy example to .env
cp .env.example .env

# Edit with your credentials
nano .env
```

### Required Environment Variables

```bash
# --- LLM Provider Selection ---
LLM_PROVIDER=ANTHROPIC  # Options: BEDROCK, OPENAI, ANTHROPIC

# --- OpenAI (if using OPENAI provider) ---
OPENAI_API_KEY=sk-your-key-here

# --- Anthropic (if using ANTHROPIC provider) ---
ANTHROPIC_API_KEY=your-anthropic-key-here

# --- AWS Bedrock (if using BEDROCK provider) ---
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# --- Vector Database (Pinecone) ---
PINECONE_API_KEY=your-pinecone-key-here
PINECONE_INDEX_NAME=clinical-rag

# --- Optional: LangChain Tracing ---
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your-langsmith-key-here
```

---

## Docker Compose Commands

### Start Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached)
docker-compose up -d

# Rebuild images and start
docker-compose up --build
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f ui

# Last 50 lines
docker-compose logs --tail=50
```

### Stop Services

```bash
# Stop running containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v
```

### Service Management

```bash
# Restart specific service
docker-compose restart api

# Run command in running container
docker-compose exec api ls -la

# Run one-off command
docker-compose run api python test_query.py
```

---

## Volume Mounting

### Data Persistence

The `data/` directory is mounted on both containers:

```yaml
volumes:
  - ./data:/app/data
```

This ensures:
- Uploaded clinical documents persist between container restarts
- Vector embeddings and chunks are accessible
- Models can cache locally

### Add Custom Volumes

Edit `docker-compose.yml` to mount additional directories:

```yaml
services:
  api:
    volumes:
      - ./data:/app/data
      - ./custom_models:/app/models  # Custom model cache
      - ./logs:/app/logs              # Log persistence
```

---

## Networking

### Internal Service Communication

Services communicate via the `clinical-rag-network`:

```yaml
services:
  api:
    networks:
      - clinical-rag-network
  ui:
    networks:
      - clinical-rag-network
    depends_on:
      - api  # UI waits for API to be healthy
```

To access the API from the UI container:
- Use service name: `http://api:8000`
- From outside: `http://localhost:8000`

---

## Health Checks

Both services implement health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s        # Check every 30 seconds
  timeout: 10s         # Wait up to 10 seconds
  retries: 3           # Allow 3 consecutive failures
  start_period: 5s     # Grace period on startup
```

Check health status:
```bash
docker-compose ps  # Shows STATUS column

# Healthy: "Up 2 minutes (healthy)"
# Unhealthy: "Up 2 minutes (unhealthy)"
```

---

## Building Custom Images

### Build Individual Image

```bash
docker build -t clinical-rag:latest .
docker run -p 8000:8000 --env-file .env clinical-rag:latest
```

### Multi-Stage Build Benefits

The Dockerfile uses two stages to optimize image size:

1. **Builder Stage:** Installs dependencies
2. **Runtime Stage:** Only copies necessary artifacts

Result:
- Smaller image size (~800MB vs 2.5GB)
- Reduced security surface area
- Faster deployment

---

## Production Deployment

### Docker Registry (Push to Registry)

```bash
# Tag image for registry
docker tag clinical-rag:latest myregistry.azurecr.io/clinical-rag:v1.0

# Push to registry
docker push myregistry.azurecr.io/clinical-rag:v1.0
```

### Scaling with Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml clinical-rag

# Scale services
docker service scale clinical-rag_api=3
```

### Kubernetes Deployment

```bash
# Generate Kubernetes manifests from compose file
kompose convert -f docker-compose.yml

# Deploy to Kubernetes
kubectl apply -f .
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Port already in use: docker-compose down
# - Missing .env file: cp .env.example .env
# - Outdated image: docker-compose down && docker-compose up --build
```

### Connection Refused Errors

```bash
# From inside container, test connection to API:
docker-compose exec ui curl http://api:8000

# From host machine:
curl http://localhost:8000
```

### Out of Memory

```bash
# Limit memory usage per container
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Permission Denied

```bash
# Delete containers and rebuild
docker-compose down -v
docker-compose up --build

# Check file permissions
ls -la data/
```

---

## Performance Tuning

### CPU/Memory Limits

Edit `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Increase verbosity for debugging

```bash
# Run with DEBUG environment variable
docker-compose -f docker-compose.yml -e DEBUG=1 up
```

---

## Security Best Practices

✅ **Implemented:**
- Non-root user (`appuser`) runs containers
- Multi-stage build reduces attack surface
- Secret management via `.env` file (not in image)
- Health checks enable automatic restarts

⚠️ **For Production:**
```bash
# Use proper secret management
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id clinical-rag/openai-key --query SecretString --output text)

# Don't commit .env
echo ".env" >> .gitignore

# Use minimal images
# Use registry authentication
docker login myregistry.azurecr.io
```

---

## Next Steps

- Test endpoints: http://localhost:8000/docs
- Upload clinical documents via http://localhost:8501
- Run evaluation: `docker-compose exec api python eval/evaluate_rag.py`
- Monitor logs: `docker-compose logs -f`

For more information, see [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
