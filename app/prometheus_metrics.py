"""
Prometheus metrics for LLM application monitoring.
Exposes metrics for collection by Prometheus.
"""
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

logger = logging.getLogger(__name__)

# Request metrics
request_count = Counter(
    'llm_request_count',
    'Total number of chat requests',
    ['user_id', 'status']
)

request_duration = Histogram(
    'llm_request_duration_seconds',
    'Request duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Quality metrics
quality_score = Gauge(
    'llm_quality_score',
    'Current quality score',
    ['metric_type']
)

# Drift metrics
drift_detected = Gauge(
    'llm_drift_detected',
    'Drift detection flag',
    ['drift_type']
)

drift_distance = Gauge(
    'llm_drift_distance',
    'Drift distance from baseline',
    ['drift_type']
)

# Anomaly metrics
anomaly_score = Gauge(
    'llm_anomaly_score',
    'Anomaly detection score'
)

# Error metrics
error_count = Counter(
    'llm_error_count',
    'Total number of errors',
    ['error_type']
)

# Response metrics
response_length = Histogram(
    'llm_response_length_chars',
    'Response length in characters',
    buckets=[50, 100, 200, 500, 1000, 2000, 5000]
)


class MetricsCollector:
    """Collects and updates Prometheus metrics."""
    
    def record_request(self, user_id: str, duration: float, status: str = "success"):
        """Record a chat request."""
        request_count.labels(user_id=user_id, status=status).inc()
        request_duration.observe(duration)
    
    def record_quality_scores(self, scores: dict):
        """Record quality evaluation scores."""
        if not scores:
            return
        
        for metric_name, score in scores.items():
            if score is not None and isinstance(score, (int, float)):
                quality_score.labels(metric_type=metric_name).set(score)
    
    def record_drift(self, drift_results: dict):
        """Record drift detection results."""
        if not drift_results:
            return
        
        # Response drift
        if "response_drift" in drift_results:
            rd = drift_results["response_drift"]
            if rd.get("drift_detected") is not None:
                drift_detected.labels(drift_type="response").set(
                    1 if rd.get("drift_detected") else 0
                )
            if rd.get("distance") is not None:
                drift_distance.labels(drift_type="response").set(rd.get("distance"))
        
        # Data drift
        if "data_drift" in drift_results:
            dd = drift_results["data_drift"]
            if dd.get("drift_detected") is not None:
                drift_detected.labels(drift_type="data").set(
                    1 if dd.get("drift_detected") else 0
                )
            if dd.get("distance") is not None:
                drift_distance.labels(drift_type="data").set(dd.get("distance"))
        
        # Quality drift
        if "quality_drift" in drift_results:
            qd = drift_results["quality_drift"]
            if qd.get("drift_detected") is not None:
                drift_detected.labels(drift_type="quality").set(
                    1 if qd.get("drift_detected") else 0
                )
    
    def record_error(self, error_type: str):
        """Record an error occurrence."""
        error_count.labels(error_type=error_type).inc()
    
    def record_response_length(self, length: int):
        """Record response text length."""
        response_length.observe(length)
    
    def record_anomaly_score(self, score: float):
        """Record anomaly detection score."""
        anomaly_score.set(score)


# Global metrics collector
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector


def get_prometheus_metrics() -> Response:
    """Generate Prometheus metrics response."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
