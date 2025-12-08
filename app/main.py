"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Responsible AI LLM Chatbot",
    description="Production-ready LLM chatbot with comprehensive monitoring",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    user_id: str = "anonymous"
    session_id: str = None
    context: dict = {}


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    metadata: dict
    timestamp: str
    session_id: str


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Responsible AI LLM Chatbot...")
    logger.info(f"Model: {os.getenv('MODEL_NAME', 'gpt-3.5-turbo')}")
    logger.info("Application started successfully!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Responsible AI LLM Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "responsible-ai-chatbot"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - processes user messages and returns LLM responses.
    
    Step 3: Includes TruLens monitoring and evaluation.
    Step 4: Includes drift detection.
    Step 5: Records Prometheus metrics.
    Step 6: Checks and triggers alerts.
    """
    start_time = datetime.utcnow()
    
    try:
        # Import here to avoid circular dependencies
        from app.chatbot import get_chatbot_response
        from app.monitor import evaluate_chat_response
        from app.drift_detector import get_drift_detector
        from app.prometheus_metrics import get_metrics_collector
        from app.alerts import get_alert_manager
        
        # Get response from chatbot
        result = await get_chatbot_response(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context
        )
        
        # Step 3: Evaluate response with TruLens
        evaluation = await evaluate_chat_response(
            input_text=request.message,
            output_text=result["response"],
            context=request.context
        )
        
        # Add evaluation to metadata
        result["metadata"]["evaluation"] = evaluation
        
        # Step 4: Detect drift
        detector = get_drift_detector()
        quality_score = evaluation.get("overall_quality")
        
        drift_results = detector.detect_all_drifts(
            input_text=request.message,
            response_text=result["response"],
            quality_score=quality_score
        )
        
        result["metadata"]["drift_detection"] = drift_results
        
        # Step 5: Record metrics
        duration = (datetime.utcnow() - start_time).total_seconds()
        metrics = get_metrics_collector()
        metrics.record_request(request.user_id, duration, "success")
        metrics.record_quality_scores(evaluation.get("scores", {}))
        metrics.record_quality_scores({"overall_quality": quality_score})
        metrics.record_drift(drift_results)
        metrics.record_response_length(len(result["response"]))
        
        # Step 6: Check alerts
        alert_manager = get_alert_manager()
        quality_alert = alert_manager.check_quality_alert(evaluation)
        drift_alert = alert_manager.check_drift_alert(drift_results)
        
        # Add alerts to metadata if triggered
        if quality_alert or drift_alert:
            result["metadata"]["alerts"] = {
                "quality_alert": quality_alert,
                "drift_alert": drift_alert
            }
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        
        # Record error metrics
        from app.prometheus_metrics import get_metrics_collector
        metrics = get_metrics_collector()
        metrics.record_error("chat_error")
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        metrics.record_request(request.user_id, duration, "error")
        
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get basic statistics about the chatbot."""
    from app.monitor import get_monitor
    
    monitor = get_monitor()
    eval_stats = monitor.get_evaluation_statistics()
    
    return {
        "model": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
        "status": "operational",
        "evaluations": eval_stats
    }


@app.get("/evaluations")
async def get_evaluations(limit: int = 10):
    """Get recent evaluation results."""
    from app.monitor import get_monitor
    
    monitor = get_monitor()
    recent = monitor.get_recent_evaluations(limit=limit)
    
    return {
        "count": len(recent),
        "evaluations": recent
    }


@app.get("/drift/status")
async def get_drift_status():
    """Get current drift detection status."""
    from app.drift_detector import get_drift_detector
    
    detector = get_drift_detector()
    return detector.get_drift_status()


@app.get("/drift/history")
async def get_drift_history(limit: int = 20):
    """Get recent drift events."""
    from app.drift_detector import get_drift_detector
    
    detector = get_drift_detector()
    history = detector.get_drift_history(limit=limit)
    
    return {
        "count": len(history),
        "drift_events": history
    }


class BaselineRequest(BaseModel):
    """Request model for setting baseline."""
    responses: List[str]
    inputs: Optional[List[str]] = None


@app.post("/drift/set-baseline")
async def set_drift_baseline(request: BaselineRequest):
    """
    Set baseline for drift detection.
    
    Provide sample responses (and optionally inputs) to establish baseline.
    """
    from app.drift_detector import get_drift_detector
    
    detector = get_drift_detector()
    detector.set_baseline(responses=request.responses, inputs=request.inputs)
    
    return {
        "status": "baseline_set",
        "response_samples": len(request.responses),
        "input_samples": len(request.inputs) if request.inputs else 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/drift/reset")
async def reset_drift_state():
    """Reset drift detection state."""
    from app.drift_detector import get_drift_detector
    
    detector = get_drift_detector()
    detector.reset_drift_state()
    
    return {
        "status": "reset_complete",
        "timestamp": datetime.utcnow().isoformat()
    }


# Step 5: Prometheus Metrics
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from app.prometheus_metrics import get_prometheus_metrics
    return get_prometheus_metrics()


# Step 6: Alert Management
@app.get("/alerts/history")
async def get_alert_history(limit: int = 20):
    """Get recent alerts."""
    from app.alerts import get_alert_manager
    
    manager = get_alert_manager()
    history = manager.get_alert_history(limit=limit)
    
    return {
        "count": len(history),
        "alerts": history
    }


@app.get("/alerts/stats")
async def get_alert_stats():
    """Get alert statistics."""
    from app.alerts import get_alert_manager
    
    manager = get_alert_manager()
    return manager.get_alert_statistics()


# Step 7: Feedback Loop
class FeedbackRequest(BaseModel):
    """Request model for feedback submission."""
    session_id: str
    feedback_type: str
    rating: Optional[int] = None
    comment: Optional[str] = None
    input_text: Optional[str] = None
    output_text: Optional[str] = None


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a chat interaction.
    
    Feedback types: quality, relevance, helpful, accurate, coherent
    Rating: 1-5 (1=poor, 5=excellent)
    """
    from app.feedback import get_feedback_processor
    
    processor = get_feedback_processor()
    
    metadata = {}
    if request.input_text:
        metadata["input"] = request.input_text
    if request.output_text:
        metadata["output"] = request.output_text
    
    feedback = processor.submit_feedback(
        session_id=request.session_id,
        feedback_type=request.feedback_type,
        rating=request.rating,
        comment=request.comment,
        metadata=metadata
    )
    
    return {
        "status": "feedback_received",
        "feedback_id": feedback.get("timestamp"),
        "message": "Thank you for your feedback!"
    }


@app.get("/feedback/summary")
async def get_feedback_summary():
    """Get feedback statistics summary."""
    from app.feedback import get_feedback_processor
    
    processor = get_feedback_processor()
    return processor.get_feedback_summary()


@app.get("/feedback/recent")
async def get_recent_feedback(limit: int = 20):
    """Get recent feedback entries."""
    from app.feedback import get_feedback_processor
    
    processor = get_feedback_processor()
    recent = processor.get_recent_feedback(limit=limit)
    
    return {
        "count": len(recent),
        "feedback": recent
    }


@app.get("/feedback/reference-dataset")
async def export_reference_dataset():
    """Export reference dataset for fine-tuning."""
    from app.feedback import get_feedback_processor
    
    processor = get_feedback_processor()
    dataset = processor.export_reference_dataset()
    
    return {
        "count": len(dataset),
        "dataset": dataset
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
