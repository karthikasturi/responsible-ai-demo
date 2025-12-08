# Day 10: Responsible AI & Comprehensive LLM Observability

## Workshop Overview

This workshop demonstrates how to build a production-ready LLM chatbot with complete observability, monitoring, and responsible AI practices. You'll learn to detect drift, monitor quality, handle anomalies, and implement automated alerting.

## What You'll Learn

- ✅ Set up a monitored LLM application with Docker
- ✅ Implement TruLens for comprehensive evaluation
- ✅ Detect response drift, data drift, and quality degradation
- ✅ Set up automated alerts (Prometheus + TruLens)
- ✅ Build a feedback loop for continuous improvement
- ✅ Deploy with monitoring dashboards (Grafana)

## Prerequisites

- Python 3.9+
- Docker & Docker Compose
- OpenAI API key (or HuggingFace token)
- Basic understanding of FastAPI and LangChain

## Project Structure

```
responsible-ai-demo/
├── README.md                       # This file
├── docker-compose.yml              # Multi-container setup
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── chatbot.py                  # LLM chatbot logic
│   ├── monitor.py                  # TruLens monitoring
│   ├── drift_detector.py           # Drift detection logic
│   ├── alerts.py                   # Alert management
│   ├── feedback.py                 # Feedback processing
│   └── prometheus_metrics.py       # Prometheus metrics
├── config/
│   ├── baseline_embeddings.json    # Baseline for drift detection
│   └── thresholds.json             # Alert thresholds
├── dashboards/
│   └── grafana-dashboard.json      # Grafana dashboard config
└── tests/
    ├── step1_test_setup.sh
    ├── step2_test_chatbot.sh
    ├── step3_test_monitoring.sh
    ├── step4_test_drift.sh
    ├── step5_test_prometheus.sh
    ├── step6_test_alerts.sh
    ├── step7_test_feedback.sh
    └── step8_complete_demo.sh
```

## Quick Start

### Step 0: Environment Preparation

```bash
# Clone and navigate to the project
cd responsible-ai-demo

# Copy environment variables
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

### Step 1: Launch the Environment

```bash
# Start all services
docker-compose up -d

# Check services are running
docker-compose ps
```

Access:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Workshop Steps

### 📘 Step 1: Environment Setup
**Goal**: Set up Docker environment with all required services

**Files**: 
- `docker-compose.yml`
- `requirements.txt`
- `.env.example`

**Duration**: 10 minutes

### 📘 Step 2: Basic LLM Chatbot
**Goal**: Create a simple FastAPI chatbot endpoint

**Files**: 
- `app/main.py`
- `app/chatbot.py`

**Test**: `bash tests/step2_test_chatbot.sh`

**Duration**: 15 minutes

### 📘 Step 3: Add Monitoring Hooks (TruLens)
**Goal**: Wrap LLM calls with TruLens evaluators

**Files**: 
- `app/monitor.py`

**Evaluators**:
- Relevance Score
- Coherence
- Response Similarity
- Groundedness

**Test**: `bash tests/step3_test_monitoring.sh`

**Duration**: 20 minutes

### 📘 Step 4: Implement Drift Detection
**Goal**: Detect response drift, data drift, and quality degradation

**Files**: 
- `app/drift_detector.py`
- `config/baseline_embeddings.json`
- `config/thresholds.json`

**Detections**:
- Response drift (embedding distance)
- Data drift (input distribution)
- Quality drift (evaluation scores)

**Test**: `bash tests/step4_test_drift.sh`

**Duration**: 25 minutes

### 📘 Step 5: Prometheus Alerts
**Goal**: Export metrics to Prometheus and visualize in Grafana

**Files**: 
- `app/prometheus_metrics.py`
- `dashboards/grafana-dashboard.json`

**Metrics**:
- `llm_quality_score`
- `llm_drift_detected`
- `llm_anomaly_score`
- `llm_request_count`
- `llm_response_time`

**Test**: `bash tests/step5_test_prometheus.sh`

**Duration**: 20 minutes

### 📘 Step 6: TruLens Alerts (Alternative)
**Goal**: Create code-based alert conditions with multiple notification channels

**Files**: 
- `app/alerts.py`

**Alert Conditions**:
- Relevance < 0.7 for 10 consecutive requests
- Embedding distance > threshold
- Toxicity or hallucination detected

**Notification Channels**:
- Slack webhook
- Email
- Console logs
- File logs

**Test**: `bash tests/step6_test_alerts.sh`

**Duration**: 20 minutes

### 📘 Step 7: Feedback Loop
**Goal**: Collect and process user feedback to improve the system

**Files**: 
- `app/feedback.py`

**Features**:
- `/feedback` endpoint
- Structured feedback storage
- Dynamic threshold adjustment
- Reference dataset enrichment

**Test**: `bash tests/step7_test_feedback.sh`

**Duration**: 15 minutes

### 📘 Step 8: End-to-End Demo
**Goal**: Run complete workflow with all features

**Files**: 
- `tests/step8_complete_demo.sh`

**Demo Flow**:
1. Normal chat interactions
2. Trigger drift simulation
3. Submit feedback
4. View metrics in Grafana
5. Review TruLens evaluations
6. Check alert notifications

**Duration**: 20 minutes

## Environment Variables

Create a `.env` file with:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-3.5-turbo

# Alternative: HuggingFace
# HUGGINGFACE_API_KEY=hf_...
# MODEL_NAME=google/flan-t5-base

# Monitoring
TRULENS_DATABASE_URL=sqlite:///./trulens.db

# Alerts (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ALERT_EMAIL=admin@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Thresholds
RELEVANCE_THRESHOLD=0.7
DRIFT_THRESHOLD=0.3
QUALITY_THRESHOLD=0.6
```

## Troubleshooting

### Issue: Docker containers won't start
```bash
docker-compose down -v
docker-compose up -d --build
```

### Issue: TruLens database locked
```bash
rm trulens.db
# Restart the application
```

### Issue: Prometheus not scraping metrics
- Check `/metrics` endpoint is accessible
- Verify prometheus.yml configuration
- Check network connectivity in Docker

### Issue: OpenAI rate limits
- Add retry logic
- Use exponential backoff
- Consider caching responses

## Best Practices

1. **Always set baselines** before monitoring drift
2. **Use appropriate thresholds** for your use case
3. **Monitor multiple metrics** (quality + drift + performance)
4. **Act on alerts** - don't just collect them
5. **Incorporate feedback** into your training loop
6. **Version your prompts** and track changes
7. **Test alert channels** before production

## Next Steps

After completing this workshop:

1. Integrate with your production LLM application
2. Customize evaluators for your domain
3. Set up proper alert escalation
4. Build automated retraining pipelines
5. Implement A/B testing with TruLens
6. Add more sophisticated drift detection
7. Create business-specific dashboards

## Resources

- [TruLens Documentation](https://www.trulens.org/trulens_eval/getting_started/)
- [LangChain Observability](https://python.langchain.com/docs/guides/evaluation/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

## License

MIT License - Feel free to use this in your workshops and projects!

## Feedback

Questions or suggestions? Open an issue or submit a PR!
