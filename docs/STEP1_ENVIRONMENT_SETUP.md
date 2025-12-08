# Step 1: Environment Setup

## Overview

In this step, you'll set up the complete Docker environment for the Responsible AI demo. This includes:

- Python application container
- Prometheus for metrics collection
- Grafana for visualization
- All necessary configurations

## What You'll Create

1. `docker-compose.yml` - Multi-container orchestration
2. `Dockerfile` - Python app container definition
3. `requirements.txt` - Python dependencies
4. `.env` - Environment variables
5. Configuration files for Prometheus and Grafana

## Step-by-Step Instructions

### 1. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your API key
nano .env
```

Add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Understand the Docker Compose Setup

Our `docker-compose.yml` defines three services:

**app**: The main Python FastAPI application
- Runs on port 8000
- Includes health checks
- Mounts volumes for live code updates
- Stores TruLens data persistently

**prometheus**: Metrics collection
- Runs on port 9090
- Scrapes metrics from the app every 15 seconds
- Stores time-series data

**grafana**: Visualization dashboards
- Runs on port 3000
- Pre-configured with Prometheus as data source
- Default credentials: admin/admin

### 3. Build and Start Services

```bash
# Build the images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:
```
NAME                    STATUS              PORTS
responsible-ai-app      Up (healthy)        0.0.0.0:8000->8000/tcp
prometheus              Up                  0.0.0.0:9090->9090/tcp
grafana                 Up                  0.0.0.0:3000->3000/tcp
```

### 4. Verify Services

**Check Application:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2025-12-05T10:30:00Z"}
```

**Check Prometheus:**
Open browser to http://localhost:9090

**Check Grafana:**
Open browser to http://localhost:3000
- Username: admin
- Password: admin

### 5. View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f app
```

## Dependencies Explained

### Core LLM Stack
- `openai` - OpenAI API client
- `langchain` - LLM framework
- `langchain-openai` - OpenAI integration for LangChain

### Monitoring & Evaluation
- `trulens-eval` - Comprehensive LLM evaluation framework
- `prometheus-client` - Export metrics to Prometheus

### Web Framework
- `fastapi` - Modern web framework for building APIs
- `uvicorn` - ASGI server for FastAPI
- `pydantic` - Data validation

### ML & Data Processing
- `sentence-transformers` - Generate embeddings for drift detection
- `scikit-learn` - ML utilities
- `numpy`, `pandas` - Data manipulation

## Project Structure Created

```
responsible-ai-demo/
├── docker-compose.yml          ✅ Multi-container setup
├── Dockerfile                  ✅ App container definition
├── requirements.txt            ✅ Python dependencies
├── .env                        ✅ Your environment variables
├── .env.example                ✅ Template
├── config/
│   ├── prometheus.yml          ✅ Prometheus configuration
│   ├── grafana-datasources.yml ✅ Grafana data sources
│   ├── baseline_embeddings.json ✅ Drift baseline storage
│   └── thresholds.json         ✅ Alert thresholds
└── app/                        (Created in Step 2)
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :9090
sudo lsof -i :3000

# Stop conflicting services or change ports in docker-compose.yml
```

### Docker Build Fails
```bash
# Clean build
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Can't Connect to Services
```bash
# Check Docker network
docker network ls
docker network inspect responsible-ai-demo_monitoring

# Restart services
docker-compose restart
```

## Key Concepts

### Why Docker Compose?
- **Isolation**: Each service runs in its own container
- **Reproducibility**: Same environment everywhere
- **Scalability**: Easy to add more services
- **Development**: Live code reload with volume mounts

### Why Prometheus?
- **Time-series**: Perfect for metrics over time
- **Pull-based**: Services expose metrics, Prometheus scrapes
- **Powerful queries**: PromQL for analysis
- **Alerting**: Built-in alert manager

### Why Grafana?
- **Visualization**: Beautiful, customizable dashboards
- **Multi-source**: Can query multiple data sources
- **Sharing**: Easy to share dashboards
- **Alerting**: Visual alert configuration

## Next Steps

✅ **Step 1 Complete!** Your environment is ready.

Proceed to **Step 2: Basic LLM Chatbot** where you'll create:
- FastAPI application structure
- `/chat` endpoint
- Simple LLM integration

## Quick Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Restart a service
docker-compose restart app

# Rebuild after code changes
docker-compose up -d --build

# Clean everything
docker-compose down -v
```

## Health Check

Before moving to Step 2, ensure:

- [ ] All three containers are running
- [ ] http://localhost:8000/health returns 200
- [ ] http://localhost:9090 shows Prometheus UI
- [ ] http://localhost:3000 shows Grafana login
- [ ] No errors in `docker-compose logs`
