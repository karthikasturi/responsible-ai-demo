# QUICKSTART GUIDE
# Day 10: Responsible AI & LLM Observability

## 🚀 5-Minute Quick Start

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key (or use mock mode)

### 1. Clone and Setup

```bash
cd responsible-ai-demo
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
nano .env
```

### 2. Launch Everything

```bash
docker-compose up -d
```

Wait ~30 seconds for services to start.

### 3. Verify Services

```bash
# Check all containers are running
docker-compose ps

# Test API
curl http://localhost:8000/health
```

### 4. Try Your First Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?", "user_id": "quickstart"}' \
  | jq
```

### 5. View Monitoring Dashboards

- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 📚 Run Workshop Steps

Each step has a test script:

```bash
# Step 2: Basic chatbot
./tests/step2_test_chatbot.sh

# Step 3: Add monitoring
./tests/step3_test_monitoring.sh

# Step 4: Drift detection
./tests/step4_test_drift.sh

# Step 5: Prometheus metrics
./tests/step5_test_prometheus.sh

# Step 6: Alert system
./tests/step6_test_alerts.sh

# Step 7: Feedback loop
./tests/step7_test_feedback.sh

# Step 8: Complete demo
./tests/step8_complete_demo.sh
```

## 🎯 Key Features Demo

### Chat with Evaluation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain supervised learning", "user_id": "demo"}' \
  | jq '.metadata.evaluation'
```

### Check Drift Status
```bash
curl http://localhost:8000/drift/status | jq
```

### View Alerts
```bash
curl http://localhost:8000/alerts/history | jq
```

### Submit Feedback
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "feedback_type": "quality",
    "rating": 5,
    "comment": "Great response!"
  }' | jq
```

### View Metrics
```bash
curl http://localhost:8000/metrics | grep llm_
```

## 🔧 Troubleshooting

### Containers won't start
```bash
docker-compose down -v
docker-compose up -d --build
```

### Check logs
```bash
docker-compose logs -f app
```

### Reset everything
```bash
docker-compose down -v
rm -rf data/* config/baseline_embeddings.json
docker-compose up -d
```

## 📖 Full Documentation

See detailed documentation in `docs/` folder:
- `STEP1_ENVIRONMENT_SETUP.md`
- `STEP2_BASIC_CHATBOT.md`
- `STEP3_MONITORING.md`
- Plus more...

## 🎓 Workshop Flow

1. **Setup** (10 min) - Get everything running
2. **Chat** (15 min) - Build basic LLM chatbot
3. **Monitor** (20 min) - Add TruLens evaluation
4. **Drift** (25 min) - Detect distribution changes
5. **Metrics** (20 min) - Prometheus & Grafana
6. **Alerts** (20 min) - Multi-channel notifications
7. **Feedback** (15 min) - Continuous improvement
8. **Demo** (20 min) - Complete workflow

Total: ~2.5 hours

## 💡 Next Steps

After the workshop:
1. Customize evaluators for your domain
2. Set up real alert channels (Slack, email)
3. Integrate with your LLM application
4. Build custom Grafana dashboards
5. Implement A/B testing
6. Add more drift detection methods

## 🆘 Need Help?

- Check service status: `docker-compose ps`
- View logs: `docker-compose logs app`
- API docs: http://localhost:8000/docs
- Full README: `README.md`

## ✅ Success Checklist

- [ ] All containers running
- [ ] `/health` returns 200
- [ ] Chat endpoint works
- [ ] Evaluations appear in responses
- [ ] Prometheus shows metrics
- [ ] Grafana accessible
- [ ] Test scripts run successfully

Happy monitoring! 🎉
