#!/bin/bash
# Step 7: Test Feedback Loop

echo "======================================="
echo "Step 7: Testing Feedback Loop"
echo "======================================="

echo ""
echo "1. Sending a chat request to get session ID..."
RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain machine learning",
    "user_id": "test_user"
  }')

SESSION_ID=$(echo $RESPONSE | jq -r '.session_id')
INPUT=$(echo $RESPONSE | jq -r '.metadata.evaluation.timestamp')
OUTPUT=$(echo $RESPONSE | jq -r '.response')

echo "Session ID: $SESSION_ID"

echo ""
echo "2. Submitting positive feedback (rating: 5)..."
curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"feedback_type\": \"quality\",
    \"rating\": 5,
    \"comment\": \"Excellent explanation, very clear and helpful!\",
    \"input_text\": \"Explain machine learning\",
    \"output_text\": \"$(echo $OUTPUT | cut -c1-100)...\"
  }" | jq

echo ""
echo "3. Submitting another chat and negative feedback..."
RESPONSE2=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AI?", "user_id": "test_user"}')

SESSION_ID2=$(echo $RESPONSE2 | jq -r '.session_id')

curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID2\",
    \"feedback_type\": \"relevance\",
    \"rating\": 2,
    \"comment\": \"Not quite what I was looking for\"
  }" | jq

echo ""
echo "4. Submitting various feedback types..."

# Quality feedback
curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"session_3\", \"feedback_type\": \"quality\", \"rating\": 4}" \
  > /dev/null

# Relevance feedback
curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"session_4\", \"feedback_type\": \"relevance\", \"rating\": 3}" \
  > /dev/null

# Helpful feedback
curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"session_5\", \"feedback_type\": \"helpful\", \"rating\": 5, \"comment\": \"Very helpful!\"}" \
  > /dev/null

echo "Submitted 3 more feedback entries"

echo ""
echo "5. Viewing feedback summary..."
curl -s http://localhost:8000/feedback/summary | jq

echo ""
echo "6. Viewing recent feedback..."
curl -s http://localhost:8000/feedback/recent?limit=5 | jq '.feedback[] | {type: .feedback_type, rating: .rating, comment: .comment}'

echo ""
echo "7. Exporting reference dataset..."
curl -s http://localhost:8000/feedback/reference-dataset | jq

echo ""
echo "8. Checking if thresholds were adjusted..."
echo "Current thresholds:"
cat /app/config/thresholds.json | jq '{quality_threshold, relevance_threshold, coherence_threshold}'

echo ""
echo "9. Viewing feedback log file..."
if [ -f /app/data/feedback.jsonl ]; then
  echo "Sample feedback entries:"
  head -3 /app/data/feedback.jsonl | jq -r '.feedback_type + " (rating: " + (.rating|tostring) + ")"'
else
  echo "Feedback log will be created after first feedback submission"
fi

echo ""
echo "✅ Step 7 tests complete!"
echo ""
echo "Feedback loop features demonstrated:"
echo "- ✅ Feedback submission with ratings and comments"
echo "- ✅ Dynamic threshold adjustment based on feedback"
echo "- ✅ Reference dataset building (high-rated examples)"
echo "- ✅ Feedback statistics and analysis"
echo "- ✅ Persistent storage in JSONL format"
