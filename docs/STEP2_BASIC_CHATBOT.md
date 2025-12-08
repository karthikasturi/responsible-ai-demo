# Step 2: Basic LLM Chatbot

## Overview

In this step, you'll create a simple but functional FastAPI-based chatbot that:

- Accepts chat messages via POST endpoint
- Uses OpenAI (or mock responses for testing)
- Returns structured responses with metadata
- Includes proper error handling
- Provides health checks

## What You'll Create

1. `app/main.py` - FastAPI application with endpoints
2. `app/chatbot.py` - LLM integration logic
3. `app/__init__.py` - Package initialization

## Architecture

```
User Request → FastAPI (/chat) → chatbot.py → OpenAI API → Response + Metadata
```

## Files Created

### `app/main.py`

Main FastAPI application with:
- **POST /chat**: Main chatbot endpoint
- **GET /health**: Health check for monitoring
- **GET /stats**: Basic statistics
- **GET /**: API information

### `app/chatbot.py`

Core chatbot logic:
- LangChain integration with OpenAI
- System prompt configuration
- Metadata collection (response time, lengths, etc.)
- Mock mode for testing without API keys
- Error handling

## Step-by-Step Instructions

### 1. Ensure Environment is Running

```bash
# Check containers are up
docker-compose ps

# If not, start them
docker-compose up -d
```

### 2. View API Documentation

Open your browser to: **http://localhost:8000/docs**

You'll see the interactive Swagger UI with all endpoints.

### 3. Test the Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00.000000",
  "service": "responsible-ai-chatbot"
}
```

### 4. Test the Chat Endpoint

**Basic Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me understand machine learning?",
    "user_id": "user123"
  }'
```

**Expected response:**
```json
{
  "response": "Hello! I'd be happy to help you understand machine learning...",
  "metadata": {
    "model": "gpt-3.5-turbo",
    "user_id": "user123",
    "processing_time_seconds": 1.23,
    "input_length": 52,
    "output_length": 245,
    "mock_mode": false
  },
  "timestamp": "2025-12-05T10:30:01.234567",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 5. Test with Session Continuity

```bash
# First message
SESSION_ID=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "user123"}' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# Follow-up message with same session
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What's the weather like?\",
    \"user_id\": \"user123\",
    \"session_id\": \"$SESSION_ID\"
  }"
```

### 6. Test with Additional Context

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain transformers in AI",
    "user_id": "user123",
    "context": {
      "topic": "machine learning",
      "level": "beginner"
    }
  }'
```

### 7. View Application Logs

```bash
# Watch logs in real-time
docker-compose logs -f app
```

You'll see log entries like:
```
INFO:app.chatbot:Processing chat request for user: user123, session: a1b2c3d4...
INFO:app.chatbot:Chat response generated in 1.23s
```

## Code Walkthrough

### Request Model (Pydantic)

```python
class ChatRequest(BaseModel):
    message: str              # Required: user's message
    user_id: str = "anonymous"  # Optional: for tracking
    session_id: str = None      # Optional: for continuity
    context: dict = {}          # Optional: additional context
```

### Response Model

```python
class ChatResponse(BaseModel):
    response: str           # LLM's response
    metadata: dict          # Processing info
    timestamp: str          # When processed
    session_id: str         # Session identifier
```

### LLM Configuration

The chatbot uses:
- **Model**: gpt-3.5-turbo (configurable via env)
- **Temperature**: 0.7 (balanced creativity/consistency)
- **System Prompt**: Professional assistant behavior

### Metadata Collected

Each response includes:
- `model`: Which LLM was used
- `user_id`: Who made the request
- `processing_time_seconds`: How long it took
- `input_length`: Character count of input
- `output_length`: Character count of output
- `mock_mode`: Whether using real API or mock

## Testing Without OpenAI API Key

If you don't have an API key yet:

1. Leave `OPENAI_API_KEY` empty in `.env`
2. The system automatically uses mock responses
3. Mock responses are labeled in metadata: `"mock_mode": true`

Example mock response:
```json
{
  "response": "Mock response to: 'Hello'. This is a test response. Please set OPENAI_API_KEY for real LLM responses.",
  "metadata": {
    "mock_mode": true,
    ...
  }
}
```

## Error Handling

The chatbot handles common errors:

**Invalid JSON:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```
Returns: 422 Unprocessable Entity

**Empty Message:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```
Returns: 422 Validation Error

**LLM API Error:**
If OpenAI API fails, returns 500 with error details.

## Key Concepts

### Why FastAPI?
- **Fast**: Built on Starlette and Pydantic
- **Auto-docs**: Swagger UI out of the box
- **Type safety**: Pydantic models enforce schema
- **Async**: Native async/await support

### Why LangChain?
- **Abstraction**: Consistent interface across LLM providers
- **Flexibility**: Easy to switch models
- **Features**: Built-in prompt management, memory, chains
- **Integration**: Works well with monitoring tools

### System Prompt
The system prompt sets the behavior:
```python
SYSTEM_PROMPT = """You are a helpful, friendly AI assistant. 
Your goal is to provide accurate, relevant, and coherent responses.
Be concise but informative. If you don't know something, say so clearly.
Always be respectful and professional."""
```

This ensures consistent, professional responses.

## Performance Considerations

Current implementation:
- **Response time**: ~1-3 seconds (depends on OpenAI)
- **Concurrency**: FastAPI handles multiple requests
- **Memory**: Stateless (no conversation history stored yet)

Later steps will add:
- Response caching
- Rate limiting
- Conversation memory
- Load balancing

## Troubleshooting

### Issue: "Import langchain_openai could not be resolved"
This is just an IDE warning. The code works fine in Docker where dependencies are installed.

### Issue: "OpenAI API Error - Rate Limit"
```bash
# Add retry logic or use mock mode temporarily
# Or upgrade your OpenAI account tier
```

### Issue: "Container keeps restarting"
```bash
# Check logs for errors
docker-compose logs app

# Common cause: Missing OPENAI_API_KEY (non-critical)
# App will use mock mode
```

### Issue: "Slow response times"
- Check your internet connection
- Verify OpenAI API status: https://status.openai.com/
- Try a different model (e.g., gpt-3.5-turbo is faster than gpt-4)

## Testing Checklist

Before moving to Step 3, verify:

- [ ] `/health` endpoint returns 200
- [ ] `/chat` endpoint accepts requests
- [ ] Responses include proper metadata
- [ ] Session IDs are generated/preserved
- [ ] Logs show processing information
- [ ] Mock mode works (if no API key)
- [ ] Real LLM works (if API key set)

## Interactive Testing with Swagger UI

1. Go to http://localhost:8000/docs
2. Click on **POST /chat**
3. Click **Try it out**
4. Enter your test data:
```json
{
  "message": "What is MLOps?",
  "user_id": "workshop-participant"
}
```
5. Click **Execute**
6. View the response

## Next Steps

✅ **Step 2 Complete!** You now have a working chatbot.

Proceed to **Step 3: Add Monitoring Hooks (TruLens)** where you'll add:
- TruLens instrumentation
- Quality evaluators (relevance, coherence)
- Response logging and analysis
- Evaluation dashboards

## Quick Reference

### Start Chatting
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Your question here", "user_id": "user123"}'
```

### Check Health
```bash
curl http://localhost:8000/health
```

### View Stats
```bash
curl http://localhost:8000/stats
```

### Watch Logs
```bash
docker-compose logs -f app
```

### Restart After Code Changes
```bash
# With auto-reload (already configured)
# Just save files - changes apply automatically

# Or manually restart
docker-compose restart app
```
