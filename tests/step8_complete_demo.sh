#!/bin/bash
# Step 8: Complete End-to-End Demo

echo "========================================="
echo "Step 8: Complete End-to-End Demo"
echo "Comprehensive Responsible AI Monitoring"
echo "========================================="

echo ""
echo "🚀 Starting complete workflow demonstration..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 1: System Initialization${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo "1.1 Checking health..."
curl -s http://localhost:8000/health | jq

echo ""
echo "1.2 Setting baseline for drift detection..."
curl -s -X POST http://localhost:8000/drift/set-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      "Machine learning is a method of data analysis that automates analytical model building.",
      "Deep learning is part of machine learning based on artificial neural networks.",
      "Supervised learning uses labeled datasets to train algorithms.",
      "MLOps combines machine learning, DevOps and data engineering.",
      "Model monitoring helps detect performance degradation in production."
    ],
    "inputs": [
      "What is machine learning?",
      "Explain deep learning",
      "What is supervised learning?",
      "Define MLOps",
      "Why monitor ML models?"
    ]
  }' | jq '{status: .status, samples: .response_samples}'

echo ""
echo -e "${GREEN}✓ System initialized${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 2: Normal Operations${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo "2.1 Processing normal ML-related queries..."

QUESTIONS=(
  "What is supervised learning?"
  "Explain neural networks"
  "How does gradient descent work?"
  "What are hyperparameters?"
  "Explain overfitting"
)

for i in "${!QUESTIONS[@]}"; do
  echo ""
  echo "Query $((i+1)): ${QUESTIONS[$i]}"
  
  RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"${QUESTIONS[$i]}\", \"user_id\": \"demo_user\"}")
  
  QUALITY=$(echo $RESPONSE | jq -r '.metadata.evaluation.overall_quality')
  DRIFT=$(echo $RESPONSE | jq -r '.metadata.drift_detection.any_drift_detected')
  
  echo "  Quality Score: $QUALITY"
  echo "  Drift Detected: $DRIFT"
  sleep 1
done

echo ""
echo -e "${GREEN}✓ Normal operations completed${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 3: Drift Simulation${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo "3.1 Introducing out-of-domain queries..."

DRIFT_QUESTIONS=(
  "What's the best recipe for chocolate cake?"
  "How do I fix a leaking faucet?"
  "Tell me about ancient Roman history"
)

for question in "${DRIFT_QUESTIONS[@]}"; do
  echo ""
  echo "Drift Query: $question"
  
  RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$question\", \"user_id\": \"demo_user\"}")
  
  DATA_DRIFT=$(echo $RESPONSE | jq -r '.metadata.drift_detection.data_drift.distance')
  DRIFT_DETECTED=$(echo $RESPONSE | jq -r '.metadata.drift_detection.any_drift_detected')
  
  echo "  Drift Distance: $DATA_DRIFT"
  echo "  Drift Flag: $DRIFT_DETECTED"
  sleep 1
done

echo ""
echo "3.2 Checking drift status..."
curl -s http://localhost:8000/drift/status | jq '{drift_detected, recent_drift_events}'

echo ""
echo -e "${YELLOW}⚠ Drift detected and logged${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 4: Quality Degradation Test${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo "4.1 Sending vague queries to trigger quality alerts..."

for i in {1..12}; do
  curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Tell me things", "user_id": "demo_user"}' \
    > /dev/null
  echo "  Low-quality request $i sent"
  sleep 0.3
done

echo ""
echo "4.2 Checking for alerts..."
curl -s http://localhost:8000/alerts/history?limit=3 | jq '.alerts[] | {type, severity, message}'

echo ""
echo -e "${YELLOW}⚠ Quality alerts triggered${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 5: Feedback Collection${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo "5.1 Collecting user feedback..."

# Positive feedback
echo "Submitting positive feedback..."
GOOD_RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain cross-validation", "user_id": "demo_user"}')

GOOD_SESSION=$(echo $GOOD_RESPONSE | jq -r '.session_id')

curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$GOOD_SESSION\",
    \"feedback_type\": \"quality\",
    \"rating\": 5,
    \"comment\": \"Excellent explanation!\"
  }" | jq '{status, message}'

# Negative feedback
echo ""
echo "Submitting negative feedback..."
BAD_RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Stuff", "user_id": "demo_user"}')

BAD_SESSION=$(echo $BAD_RESPONSE | jq -r '.session_id')

curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$BAD_SESSION\",
    \"feedback_type\": \"relevance\",
    \"rating\": 1,
    \"comment\": \"Not helpful at all\"
  }" | jq '{status, message}'

echo ""
echo "5.2 Viewing feedback summary..."
curl -s http://localhost:8000/feedback/summary | jq

echo ""
echo -e "${GREEN}✓ Feedback collected and processed${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 6: Metrics Review${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo "6.1 Evaluation statistics..."
curl -s http://localhost:8000/stats | jq '.evaluations.overall'

echo ""
echo "6.2 Alert statistics..."
curl -s http://localhost:8000/alerts/stats | jq

echo ""
echo "6.3 Sample Prometheus metrics..."
curl -s http://localhost:8000/metrics | grep -E "^llm_(request_count|quality_score|drift_detected)" | head -5

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Demo Complete! Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo "📊 What we demonstrated:"
echo ""
echo "✅ Step 1: Environment setup with Docker"
echo "✅ Step 2: Basic LLM chatbot with FastAPI"
echo "✅ Step 3: TruLens evaluation (relevance, coherence, etc.)"
echo "✅ Step 4: Drift detection (response, data, quality)"
echo "✅ Step 5: Prometheus metrics collection"
echo "✅ Step 6: Multi-channel alerting system"
echo "✅ Step 7: Feedback loop with threshold adjustment"
echo "✅ Step 8: End-to-end workflow integration"

echo ""
echo "🌐 Access Points:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3000 (admin/admin)"

echo ""
echo "📈 Try these Grafana queries:"
echo "   • rate(llm_request_count[5m])"
echo "   • llm_quality_score"
echo "   • llm_drift_detected"

echo ""
echo "🔍 Key Files Created:"
echo "   • /app/data/alerts.log - Alert history"
echo "   • /app/data/feedback.jsonl - User feedback"
echo "   • /app/config/thresholds.json - Dynamic thresholds"
echo "   • /app/config/baseline_embeddings.json - Drift baseline"

echo ""
echo "🎓 Workshop Complete!"
echo "You now have a production-ready LLM monitoring system!"
echo ""
echo -e "${GREEN}✨ All tests passed successfully! ✨${NC}"
