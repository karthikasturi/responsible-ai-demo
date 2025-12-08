# API Reference Guide
# Responsible AI LLM Chatbot

Complete API documentation for all endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (add in production).

---

## Core Endpoints

### GET /
**Description**: API information and welcome message

**Response**:
```json
{
  "message": "Responsible AI LLM Chatbot API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### GET /health
**Description**: Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00.000000",
  "service": "responsible-ai-chatbot"
}
```

---

## Chat Endpoints

### POST /chat
**Description**: Main chatbot endpoint with full monitoring

**Request Body**:
```json
{
  "message": "Your question here",
  "user_id": "user123",
  "session_id": "optional-session-id",
  "context": {}
}
```

**Response**:
```json
{
  "response": "LLM generated response",
  "metadata": {
    "model": "gpt-3.5-turbo",
    "user_id": "user123",
    "processing_time_seconds": 1.23,
    "input_length": 20,
    "output_length": 150,
    "evaluation": {
      "evaluations_available": true,
      "scores": {
        "relevance": 0.95,
        "coherence": 0.88,
        "groundedness": 0.82,
        "sentiment": 0.75,
        "conciseness": 0.80
      },
      "overall_quality": 0.84
    },
    "drift_detection": {
      "response_drift": {
        "drift_detected": false,
        "distance": 0.12
      },
      "data_drift": {
        "drift_detected": false,
        "distance": 0.08
      },
      "any_drift_detected": false
    }
  },
  "timestamp": "2025-12-05T10:30:01.000000",
  "session_id": "abc123-def456"
}
```

---

## Monitoring Endpoints

### GET /stats
**Description**: Get overall system statistics

**Response**:
```json
{
  "model": "gpt-3.5-turbo",
  "status": "operational",
  "evaluations": {
    "relevance": {
      "mean": 0.87,
      "std": 0.12,
      "min": 0.65,
      "max": 0.98,
      "count": 100
    },
    "overall": {
      "mean": 0.81,
      "std": 0.11,
      "count": 100
    },
    "total_evaluations": 100
  }
}
```

### GET /evaluations
**Description**: Get recent evaluation results

**Query Parameters**:
- `limit` (optional, default=10): Number of evaluations to return

**Response**:
```json
{
  "count": 10,
  "evaluations": [
    {
      "timestamp": "2025-12-05T10:30:00.000000",
      "scores": {
        "relevance": 0.95,
        "coherence": 0.88
      },
      "overall_quality": 0.84
    }
  ]
}
```

---

## Drift Detection Endpoints

### GET /drift/status
**Description**: Get current drift detection status

**Response**:
```json
{
  "drift_detected": {
    "response_drift": false,
    "data_drift": false,
    "quality_drift": false
  },
  "recent_drift_events": 3,
  "total_drift_events": 15,
  "sample_counts": {
    "responses": 100,
    "inputs": 100,
    "quality_scores": 100
  },
  "baseline_status": {
    "response_baseline_set": true,
    "input_baseline_set": true,
    "baseline_age": "2025-12-05T09:00:00.000000"
  }
}
```

### GET /drift/history
**Description**: Get recent drift events

**Query Parameters**:
- `limit` (optional, default=20): Number of events to return

**Response**:
```json
{
  "count": 5,
  "drift_events": [
    {
      "type": "response_drift",
      "drift_detected": true,
      "distance": 0.45,
      "threshold": 0.4,
      "timestamp": "2025-12-05T10:25:00.000000"
    }
  ]
}
```

### POST /drift/set-baseline
**Description**: Set baseline for drift detection

**Request Body**:
```json
{
  "responses": [
    "Sample response 1",
    "Sample response 2",
    "Sample response 3"
  ],
  "inputs": [
    "Sample input 1",
    "Sample input 2"
  ]
}
```

**Response**:
```json
{
  "status": "baseline_set",
  "response_samples": 3,
  "input_samples": 2,
  "timestamp": "2025-12-05T10:30:00.000000"
}
```

### POST /drift/reset
**Description**: Reset drift detection state

**Response**:
```json
{
  "status": "reset_complete",
  "timestamp": "2025-12-05T10:30:00.000000"
}
```

---

## Alert Endpoints

### GET /alerts/history
**Description**: Get recent alerts

**Query Parameters**:
- `limit` (optional, default=20): Number of alerts to return

**Response**:
```json
{
  "count": 5,
  "alerts": [
    {
      "type": "quality_degradation",
      "severity": "high",
      "metric": "relevance",
      "value": 0.55,
      "threshold": 0.7,
      "message": "Relevance below threshold",
      "timestamp": "2025-12-05T10:28:00.000000"
    }
  ]
}
```

### GET /alerts/stats
**Description**: Get alert statistics

**Response**:
```json
{
  "total_alerts": 25,
  "by_type": {
    "quality_degradation": 15,
    "drift_detected": 10
  },
  "by_severity": {
    "high": 18,
    "medium": 7
  },
  "recent_count": 5
}
```

---

## Feedback Endpoints

### POST /feedback
**Description**: Submit user feedback

**Request Body**:
```json
{
  "session_id": "abc123-def456",
  "feedback_type": "quality",
  "rating": 5,
  "comment": "Excellent response!",
  "input_text": "What is ML?",
  "output_text": "Machine learning is..."
}
```

**Feedback Types**:
- `quality` - Overall response quality
- `relevance` - How relevant to the question
- `helpful` - How helpful the response was
- `accurate` - Accuracy of information
- `coherent` - Logical consistency

**Rating Scale**: 1-5 (1=poor, 5=excellent)

**Response**:
```json
{
  "status": "feedback_received",
  "feedback_id": "2025-12-05T10:30:00.000000",
  "message": "Thank you for your feedback!"
}
```

### GET /feedback/summary
**Description**: Get feedback statistics

**Response**:
```json
{
  "total_feedback": 50,
  "average_rating": 4.2,
  "rating_distribution": {
    "5": 25,
    "4": 15,
    "3": 5,
    "2": 3,
    "1": 2
  },
  "feedback_by_type": {
    "quality": 20,
    "relevance": 15,
    "helpful": 15
  },
  "reference_dataset_size": 30
}
```

### GET /feedback/recent
**Description**: Get recent feedback entries

**Query Parameters**:
- `limit` (optional, default=20): Number of entries to return

**Response**:
```json
{
  "count": 10,
  "feedback": [
    {
      "session_id": "abc123",
      "feedback_type": "quality",
      "rating": 5,
      "comment": "Great!",
      "timestamp": "2025-12-05T10:30:00.000000"
    }
  ]
}
```

### GET /feedback/reference-dataset
**Description**: Export reference dataset for fine-tuning

**Response**:
```json
{
  "count": 30,
  "dataset": [
    {
      "input": "What is machine learning?",
      "output": "Machine learning is...",
      "rating": 5,
      "timestamp": "2025-12-05T10:00:00.000000"
    }
  ]
}
```

---

## Metrics Endpoint

### GET /metrics
**Description**: Prometheus metrics in text format

**Response Format**: Prometheus text exposition format

**Sample Metrics**:
```
# HELP llm_request_count Total number of chat requests
# TYPE llm_request_count counter
llm_request_count{user_id="user1",status="success"} 150.0

# HELP llm_quality_score Current quality score
# TYPE llm_quality_score gauge
llm_quality_score{metric_type="overall_quality"} 0.84

# HELP llm_drift_detected Drift detection flag
# TYPE llm_drift_detected gauge
llm_drift_detected{drift_type="response"} 0.0
llm_drift_detected{drift_type="data"} 0.0

# HELP llm_request_duration_seconds Request duration
# TYPE llm_request_duration_seconds histogram
llm_request_duration_seconds_bucket{le="0.5"} 25.0
llm_request_duration_seconds_bucket{le="1.0"} 80.0
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Chat processing failed: [error details]"
}
```

---

## Rate Limiting

Currently not implemented. In production, consider:
- Per-user rate limits
- IP-based throttling
- Token bucket algorithm

---

## Best Practices

### 1. Session Management
Always pass `session_id` for conversation continuity:
```bash
# First message
SESSION=$(curl -X POST .../chat -d '{"message": "Hi"}' | jq -r '.session_id')

# Follow-up
curl -X POST .../chat -d "{\"message\": \"More questions\", \"session_id\": \"$SESSION\"}"
```

### 2. Error Handling
Always check response status:
```python
response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
else:
    print(f"Error: {response.status_code}")
```

### 3. Monitoring
Regularly check drift and quality:
```bash
# Check every hour
*/60 * * * * curl -s localhost:8000/drift/status | jq
```

### 4. Feedback Collection
Collect feedback for quality improvement:
```python
# After showing response to user
if user_rating:
    submit_feedback(session_id, "quality", user_rating)
```

---

## Interactive API Documentation

Visit http://localhost:8000/docs for:
- Interactive testing
- Auto-generated documentation
- Request/response examples
- Try-it-out functionality

---

## SDK Examples

### Python
```python
import requests

API_URL = "http://localhost:8000"

# Chat
response = requests.post(
    f"{API_URL}/chat",
    json={"message": "What is ML?", "user_id": "user1"}
)
print(response.json()["response"])

# Check drift
drift = requests.get(f"{API_URL}/drift/status")
print(drift.json())

# Submit feedback
feedback = requests.post(
    f"{API_URL}/feedback",
    json={
        "session_id": response.json()["session_id"],
        "feedback_type": "quality",
        "rating": 5
    }
)
```

### JavaScript
```javascript
const API_URL = "http://localhost:8000";

// Chat
const response = await fetch(`${API_URL}/chat`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    message: "What is ML?",
    user_id: "user1"
  })
});
const data = await response.json();
console.log(data.response);
```

### cURL
```bash
# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ML?", "user_id": "user1"}'

# Get stats
curl http://localhost:8000/stats | jq

# Submit feedback
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc", "feedback_type": "quality", "rating": 5}'
```

---

## Troubleshooting

### Connection Refused
```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs app
```

### Slow Responses
```bash
# Check processing time
curl localhost:8000/stats | jq '.evaluations'

# Check Prometheus metrics
curl localhost:8000/metrics | grep duration
```

### Evaluation Failures
```bash
# Check OpenAI API key
docker-compose exec app env | grep OPENAI

# Check TruLens status
curl localhost:8000/evaluations | jq
```

---

For more information, see:
- Main documentation: `README.md`
- Quick start: `QUICKSTART.md`
- Step-by-step guides: `docs/` folder
