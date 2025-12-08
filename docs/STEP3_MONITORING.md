# Step 3: Add Monitoring Hooks (TruLens)

## Overview

In this step, you'll wrap your LLM calls with TruLens evaluation to monitor:

- **Relevance**: Does the response address the user's question?
- **Coherence**: Is the response logically consistent?
- **Groundedness**: Is the response grounded in facts?
- **Sentiment**: What's the tone of the response?
- **Conciseness**: Is the response appropriately concise?

## What You'll Create

1. `app/monitor.py` - TruLens integration and evaluation logic
2. Updated `app/main.py` - Integrate monitoring into chat endpoint
3. New endpoints for viewing evaluations

## Architecture

```
User → /chat → Chatbot → LLM Response → TruLens Evaluation → Response + Metrics
```

## Files Modified/Created

### `app/monitor.py` (New)

Core monitoring functionality:
- `TruLensMonitor` class
- Feedback function setup
- Evaluation execution
- Statistics collection

### `app/main.py` (Modified)

Added:
- TruLens evaluation in `/chat` endpoint
- `/evaluations` endpoint for viewing results
- Enhanced `/stats` with evaluation statistics

## Step-by-Step Instructions

### 1. Restart Services

```bash
# Rebuild to include new code
docker-compose restart app

# Watch logs
docker-compose logs -f app
```

### 2. Test Basic Chat with Evaluation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "user_id": "user123"
  }' | jq
```

**Expected response now includes evaluation:**
```json
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "metadata": {
    "model": "gpt-3.5-turbo",
    "processing_time_seconds": 1.45,
    "evaluation": {
      "evaluations_available": true,
      "timestamp": "2025-12-05T10:30:00.000000",
      "scores": {
        "relevance": 0.95,
        "coherence": 0.88,
        "groundedness": 0.82,
        "sentiment": 0.75,
        "conciseness": 0.80
      },
      "overall_quality": 0.84
    }
  },
  "timestamp": "2025-12-05T10:30:00.000000",
  "session_id": "abc123..."
}
```

### 3. View Recent Evaluations

```bash
# Get last 5 evaluations
curl "http://localhost:8000/evaluations?limit=5" | jq
```

Expected response:
```json
{
  "count": 5,
  "evaluations": [
    {
      "evaluations_available": true,
      "timestamp": "2025-12-05T10:30:00.000000",
      "scores": {
        "relevance": 0.95,
        "coherence": 0.88,
        ...
      },
      "overall_quality": 0.84
    },
    ...
  ]
}
```

### 4. View Evaluation Statistics

```bash
curl http://localhost:8000/stats | jq
```

Expected response:
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
      "count": 15
    },
    "coherence": {
      "mean": 0.82,
      "std": 0.09,
      ...
    },
    "overall": {
      "mean": 0.81,
      "std": 0.11,
      "min": 0.62,
      "max": 0.94,
      "count": 15
    },
    "total_evaluations": 15
  }
}
```

### 5. Test Multiple Queries to Build Statistics

```bash
# Test script to generate multiple evaluations
for message in \
  "What is AI?" \
  "Explain neural networks" \
  "How does deep learning work?" \
  "What are transformers?" \
  "Explain MLOps"
do
  echo "Testing: $message"
  curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$message\", \"user_id\": \"tester\"}" \
    | jq '.metadata.evaluation.overall_quality'
  sleep 2
done
```

### 6. Compare Good vs Poor Quality Responses

**High Quality Question:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the difference between supervised and unsupervised learning with examples",
    "user_id": "user123"
  }' | jq '.metadata.evaluation'
```

Expected: High relevance, coherence, groundedness (0.8-0.95)

**Ambiguous Question:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about that thing",
    "user_id": "user123"
  }' | jq '.metadata.evaluation'
```

Expected: Lower relevance and coherence scores (0.4-0.7)

## Understanding the Evaluation Metrics

### Relevance Score (0-1)
- **Measures**: How well the response addresses the input question
- **High (0.8-1.0)**: Response directly answers the question
- **Medium (0.5-0.79)**: Response is somewhat related
- **Low (0-0.49)**: Response doesn't address the question

### Coherence Score (0-1)
- **Measures**: Logical consistency and flow of the response
- **High (0.8-1.0)**: Clear, well-structured, logical
- **Medium (0.5-0.79)**: Mostly coherent with minor issues
- **Low (0-0.49)**: Confusing or contradictory

### Groundedness Score (0-1)
- **Measures**: Whether response is based on factual information
- **High (0.8-1.0)**: Well-grounded, factual statements
- **Medium (0.5-0.79)**: Mostly grounded with some speculation
- **Low (0-0.49)**: Speculative or potentially hallucinated

### Sentiment Score (-1 to 1)
- **Measures**: Emotional tone of the response
- **Positive (0.5-1.0)**: Friendly, encouraging tone
- **Neutral (0.0-0.49)**: Professional, objective tone
- **Negative (-1.0 to -0.01)**: Critical or negative tone

### Conciseness Score (0-1)
- **Measures**: Appropriate length for the question
- **High (0.8-1.0)**: Right amount of detail
- **Medium (0.5-0.79)**: Slightly verbose or brief
- **Low (0-0.49)**: Too long or too short

### Overall Quality Score (0-1)
- **Calculation**: Average of all metric scores
- **Good (0.75-1.0)**: High-quality response
- **Acceptable (0.6-0.74)**: Adequate but could improve
- **Poor (0-0.59)**: Needs improvement

## Code Walkthrough

### TruLensMonitor Class

```python
class TruLensMonitor:
    def __init__(self):
        # Initialize TruLens connection
        self.tru = tru
        self.provider = openai_provider
        
        # Set up feedback functions
        self._setup_feedback_functions()
```

### Feedback Functions Setup

```python
def _setup_feedback_functions(self):
    # Create feedback functions for each metric
    f_relevance = Feedback(
        self.provider.relevance,
        name="Relevance"
    ).on_input_output()
    
    # ... more feedback functions
```

### Evaluation Execution

```python
def evaluate_response(self, input_text, output_text, context):
    # Run each feedback function
    for feedback in self.feedback_functions:
        score = self.provider.relevance(input_text, output_text)
        results["scores"][feedback.name.lower()] = float(score)
    
    # Calculate overall quality
    results["overall_quality"] = mean(valid_scores)
```

## Integration with Main App

The `/chat` endpoint now:
1. Gets chatbot response (Step 2)
2. **NEW**: Evaluates response with TruLens
3. **NEW**: Adds evaluation to metadata
4. Returns enhanced response

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # Get chatbot response
    result = await get_chatbot_response(...)
    
    # Evaluate response
    evaluation = await evaluate_chat_response(
        input_text=request.message,
        output_text=result["response"],
        context=request.context
    )
    
    # Add to metadata
    result["metadata"]["evaluation"] = evaluation
    
    return ChatResponse(**result)
```

## TruLens Database

TruLens stores evaluation data in SQLite:
- **Location**: `trulens.db` in app directory
- **Schema**: Evaluations, feedback records, app metadata
- **Access**: Via TruLens API or direct SQL

### View Database Contents

```bash
# Enter app container
docker-compose exec app bash

# Open database
sqlite3 trulens.db

# View tables
.tables

# View recent evaluations
SELECT * FROM feedbacks LIMIT 5;

# Exit
.quit
exit
```

## Performance Impact

Adding TruLens evaluation:
- **Additional time**: ~0.5-2 seconds per request
- **API calls**: 5 additional OpenAI calls (one per metric)
- **Cost**: ~$0.001-0.002 per evaluation (with GPT-3.5-turbo)

**Optimization tips:**
- Run evaluations asynchronously
- Sample evaluations (not every request)
- Use batch evaluation for historical data
- Cache evaluation results

## Troubleshooting

### Issue: "OpenAI provider not available"
```bash
# Check API key is set
docker-compose exec app printenv | grep OPENAI_API_KEY

# Restart with correct key
# Edit .env, then:
docker-compose restart app
```

### Issue: Evaluations return null scores
- Check OpenAI API quota/credits
- Verify API key has correct permissions
- Check network connectivity

### Issue: Slow evaluation times
- Evaluations are sequential - consider async
- Use sampling: evaluate 10% of requests
- Cache results for identical inputs

### Issue: Database locked errors
```bash
# Stop app
docker-compose stop app

# Remove lock
docker-compose exec app rm -f trulens.db-journal

# Restart
docker-compose start app
```

## Best Practices

### 1. Sampling Strategy
Don't evaluate every request in production:
```python
import random
if random.random() < 0.1:  # 10% sampling
    evaluation = await evaluate_chat_response(...)
```

### 2. Async Evaluation
Run evaluations in background:
```python
import asyncio
asyncio.create_task(evaluate_chat_response(...))
```

### 3. Threshold Alerts
Set quality thresholds:
```python
if evaluation["overall_quality"] < 0.6:
    logger.warning("Low quality response detected!")
    # Trigger alert
```

### 4. Trend Monitoring
Track metrics over time:
```python
stats = monitor.get_evaluation_statistics()
if stats["overall"]["mean"] < 0.7:
    logger.warning("Quality degradation detected!")
```

## Testing Checklist

Before moving to Step 4, verify:

- [ ] Chat responses include evaluation metadata
- [ ] All 5 metrics are calculated (relevance, coherence, etc.)
- [ ] `/evaluations` endpoint returns results
- [ ] `/stats` shows evaluation statistics
- [ ] Overall quality score is computed
- [ ] Evaluation results are stored
- [ ] Multiple requests build statistics

## Interactive Testing

### Using Swagger UI

1. Go to http://localhost:8000/docs
2. Try POST `/chat` with various messages
3. Check evaluation scores in response
4. Try GET `/evaluations` to see history
5. Try GET `/stats` to see aggregated statistics

### Using Python

```python
import requests

# Send chat request
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What is MLOps?",
        "user_id": "tester"
    }
)

# Extract evaluation
evaluation = response.json()["metadata"]["evaluation"]
print(f"Quality Score: {evaluation['overall_quality']}")
print(f"Relevance: {evaluation['scores']['relevance']}")
```

## Next Steps

✅ **Step 3 Complete!** Your chatbot now has comprehensive evaluation.

Proceed to **Step 4: Implement Drift Detection** where you'll add:
- Response drift detection (embedding-based)
- Data drift detection (input distribution)
- Quality drift detection (evaluation trends)
- Baseline management
- Drift alerting

## Quick Reference

### View Latest Evaluation
```bash
curl -s http://localhost:8000/evaluations?limit=1 | jq '.evaluations[0]'
```

### Check Overall Quality Trend
```bash
curl -s http://localhost:8000/stats | jq '.evaluations.overall.mean'
```

### Test Quality with Different Questions
```bash
# Good question (expect high scores)
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is supervised learning?"}' \
  | jq '.metadata.evaluation.overall_quality'

# Vague question (expect lower scores)
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me stuff"}' \
  | jq '.metadata.evaluation.overall_quality'
```
