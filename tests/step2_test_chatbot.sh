#!/bin/bash
# Step 2: Test Basic Chatbot

echo "======================================="
echo "Step 2: Testing Basic Chatbot"
echo "======================================="

echo ""
echo "1. Testing health endpoint..."
curl -s http://localhost:8000/health | jq

echo ""
echo "2. Testing basic chat..."
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What is machine learning?",
    "user_id": "test_user"
  }' | jq '.response, .metadata.processing_time_seconds'

echo ""
echo "3. Testing chat with session..."
SESSION_ID=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi there", "user_id": "test_user"}' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What can you help me with?\", \"user_id\": \"test_user\", \"session_id\": \"$SESSION_ID\"}" \
  | jq '.response'

echo ""
echo "4. Testing stats endpoint..."
curl -s http://localhost:8000/stats | jq

echo ""
echo "✅ Step 2 tests complete!"
