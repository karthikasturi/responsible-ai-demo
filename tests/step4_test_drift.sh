#!/bin/bash
# Step 4: Test Drift Detection

echo "======================================="
echo "Step 4: Testing Drift Detection"
echo "======================================="

echo ""
echo "1. Setting baseline with sample responses..."
curl -s -X POST http://localhost:8000/drift/set-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      "Machine learning is a subset of AI that enables systems to learn from data.",
      "Neural networks are computing systems inspired by biological neural networks.",
      "Deep learning uses multiple layers to progressively extract features from raw input.",
      "Supervised learning uses labeled data to train models.",
      "Gradient descent is an optimization algorithm to minimize the loss function."
    ],
    "inputs": [
      "What is machine learning?",
      "Explain neural networks",
      "What is deep learning?",
      "Define supervised learning",
      "How does gradient descent work?"
    ]
  }' | jq

echo ""
echo "2. Normal request (should not trigger drift)..."
RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is artificial intelligence?",
    "user_id": "test_user"
  }')

echo "Drift Detection:"
echo $RESPONSE | jq '.metadata.drift_detection'

echo ""
echo "3. Checking drift status..."
curl -s http://localhost:8000/drift/status | jq

echo ""
echo "4. Simulating drift with very different topic..."
DRIFT_RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about cooking pasta and Italian cuisine traditions",
    "user_id": "test_user"
  }')

echo "Drift Detection (should show higher distance):"
echo $DRIFT_RESPONSE | jq '.metadata.drift_detection'

echo ""
echo "5. Multiple drift-inducing requests..."
for topic in \
  "Explain quantum physics" \
  "How to build a house" \
  "What is the history of Rome?" \
  "Cooking recipes for beginners"
do
  echo "Testing: $topic"
  DRIFT=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$topic\", \"user_id\": \"test_user\"}" \
    | jq -r '.metadata.drift_detection.data_drift.distance')
  echo "  Drift Distance: $DRIFT"
  sleep 1
done

echo ""
echo "6. Viewing drift history..."
curl -s http://localhost:8000/drift/history?limit=5 | jq

echo ""
echo "7. Final drift status..."
curl -s http://localhost:8000/drift/status | jq

echo ""
echo "✅ Step 4 tests complete!"
