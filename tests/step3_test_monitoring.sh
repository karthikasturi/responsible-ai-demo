#!/bin/bash
# Step 3: Test TruLens Monitoring

echo "======================================="
echo "Step 3: Testing TruLens Monitoring"
echo "======================================="

echo ""
echo "1. Sending chat request with evaluation..."
RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain supervised learning in simple terms",
    "user_id": "test_user"
  }')

echo "Response: $(echo $RESPONSE | jq -r '.response' | cut -c1-100)..."
echo ""
echo "Evaluation Scores:"
echo $RESPONSE | jq '.metadata.evaluation.scores'
echo ""
echo "Overall Quality: $(echo $RESPONSE | jq -r '.metadata.evaluation.overall_quality')"

echo ""
echo "2. Testing multiple questions to build statistics..."
for question in \
  "What is AI?" \
  "Explain neural networks" \
  "How does deep learning work?" \
  "What are transformers in ML?" \
  "Explain gradient descent"
do
  echo "Testing: $question"
  QUALITY=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$question\", \"user_id\": \"test_user\"}" \
    | jq -r '.metadata.evaluation.overall_quality')
  echo "  Quality Score: $QUALITY"
  sleep 1
done

echo ""
echo "3. Viewing evaluation statistics..."
curl -s http://localhost:8000/stats | jq '.evaluations'

echo ""
echo "4. Viewing recent evaluations..."
curl -s http://localhost:8000/evaluations?limit=3 | jq '.evaluations[].scores'

echo ""
echo "✅ Step 3 tests complete!"
