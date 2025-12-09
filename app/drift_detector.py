"""
Drift detection for LLM responses and inputs.
Detects response drift, data drift, and quality degradation.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import deque

logger = logging.getLogger(__name__)

# Configuration paths
BASELINE_PATH = "/app/config/baseline_embeddings.json"
THRESHOLDS_PATH = "/app/config/thresholds.json"

# Initialize embedding model
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Sentence transformer model loaded")
except Exception as e:
    logger.error(f"Could not load sentence transformer: {e}")
    embedding_model = None


class DriftDetector:
    """
    Detects various types of drift in LLM applications:
    - Response drift: Changes in output embedding distribution
    - Data drift: Changes in input distribution
    - Quality drift: Degradation in evaluation metrics
    """
    
    def __init__(self):
        """Initialize drift detector."""
        self.baseline = self._load_baseline()
        self.thresholds = self._load_thresholds()
        
        # History buffers (using deque for efficiency)
        self.response_embeddings = deque(maxlen=100)
        self.input_embeddings = deque(maxlen=100)
        self.quality_scores = deque(maxlen=100)
        
        # Drift state tracking
        self.drift_detected = {
            "response_drift": False,
            "data_drift": False,
            "quality_drift": False
        }
        
        self.drift_history = []
        
    def _load_baseline(self) -> Dict:
        """Load baseline embeddings from file."""
        try:
            if os.path.exists(BASELINE_PATH):
                with open(BASELINE_PATH, 'r') as f:
                    baseline = json.load(f)
                logger.info("Baseline embeddings loaded")
                return baseline
            else:
                logger.warning("No baseline found, will create on first use")
                return {
                    "baseline_embedding": None,
                    "baseline_timestamp": None,
                    "baseline_version": "1.0",
                    "baseline_samples": []
                }
        except Exception as e:
            logger.error(f"Error loading baseline: {e}")
            return {}
    
    def _save_baseline(self):
        """Save baseline embeddings to file."""
        try:
            os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
            with open(BASELINE_PATH, 'w') as f:
                json.dump(self.baseline, f, indent=2)
            logger.info("Baseline embeddings saved")
        except Exception as e:
            logger.error(f"Error saving baseline: {e}")
    
    def _load_thresholds(self) -> Dict:
        """Load detection thresholds from file."""
        try:
            if os.path.exists(THRESHOLDS_PATH):
                with open(THRESHOLDS_PATH, 'r') as f:
                    thresholds = json.load(f)
                logger.info("Thresholds loaded")
                return thresholds
            else:
                # Default thresholds
                return {
                    "drift_threshold": 0.3,
                    "quality_threshold": 0.6,
                    "embedding_distance_threshold": 0.4
                }
        except Exception as e:
            logger.error(f"Error loading thresholds: {e}")
            return {}
    
    def set_baseline(self, responses: List[str], inputs: Optional[List[str]] = None):
        """
        Set baseline embeddings from sample responses and inputs.
        
        Args:
            responses: List of response texts to use as baseline
            inputs: Optional list of input texts for data drift baseline
        """
        if not embedding_model:
            logger.error("Embedding model not available")
            return
        
        try:
            # Generate embeddings for responses
            response_embeddings = embedding_model.encode(responses)
            baseline_embedding = np.mean(response_embeddings, axis=0)
            
            self.baseline = {
                "baseline_embedding": baseline_embedding.tolist(),
                "baseline_timestamp": datetime.utcnow().isoformat(),
                "baseline_version": "1.0",
                "baseline_samples": responses[:5],  # Store first 5 samples
                "sample_count": len(responses)
            }
            
            # Add input baseline if provided
            if inputs:
                input_embeddings = embedding_model.encode(inputs)
                input_baseline = np.mean(input_embeddings, axis=0)
                self.baseline["input_baseline_embedding"] = input_baseline.tolist()
                self.baseline["input_sample_count"] = len(inputs)
            
            self._save_baseline()
            logger.info(f"Baseline set with {len(responses)} response samples")
            
        except Exception as e:
            logger.error(f"Error setting baseline: {e}")
    
    def detect_response_drift(self, response_text: str) -> Dict:
        """
        Detect drift in response using embedding distance.
        
        Args:
            response_text: The LLM response to check
            
        Returns:
            Dictionary with drift detection results
        """
        if not embedding_model:
            return {"drift_detected": False, "reason": "Embedding model not available"}
        
        if not self.baseline.get("baseline_embedding"):
            return {"drift_detected": False, "reason": "No baseline set"}
        
        try:
            # Generate embedding for current response
            current_embedding = embedding_model.encode([response_text])[0]
            
            # Store in history
            self.response_embeddings.append(current_embedding)
            
            # Calculate distance from baseline
            baseline_emb = np.array(self.baseline["baseline_embedding"])
            distance = 1 - cosine_similarity(
                [current_embedding],
                [baseline_emb]
            )[0][0]
            
            # Check threshold
            threshold = self.thresholds.get("embedding_distance_threshold", 0.4)
            drift_detected = distance > threshold
            
            result = {
                "drift_detected": bool(drift_detected),
                "distance": float(distance),
                "threshold": threshold,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "response_drift"
            }
            
            if drift_detected:
                logger.warning(f"Response drift detected! Distance: {distance:.3f}")
                self.drift_detected["response_drift"] = True
                self.drift_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting response drift: {e}")
            return {"drift_detected": False, "error": str(e)}
    
    def detect_data_drift(self, input_text: str) -> Dict:
        """
        Detect drift in input distribution.
        
        Args:
            input_text: The user input to check
            
        Returns:
            Dictionary with drift detection results
        """
        if not embedding_model:
            return {"drift_detected": False, "reason": "Embedding model not available"}
        
        if not self.baseline.get("input_baseline_embedding"):
            return {"drift_detected": False, "reason": "No input baseline set"}
        
        try:
            # Generate embedding for current input
            current_embedding = embedding_model.encode([input_text])[0]
            
            # Store in history
            self.input_embeddings.append(current_embedding)
            
            # Calculate distance from baseline
            baseline_emb = np.array(self.baseline["input_baseline_embedding"])
            distance = 1 - cosine_similarity(
                [current_embedding],
                [baseline_emb]
            )[0][0]
            
            # Check threshold
            threshold = self.thresholds.get("drift_threshold", 0.3)
            drift_detected = distance > threshold
            
            result = {
                "drift_detected": bool(drift_detected),
                "distance": float(distance),
                "threshold": threshold,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "data_drift"
            }
            
            if drift_detected:
                logger.warning(f"Data drift detected! Distance: {distance:.3f}")
                self.drift_detected["data_drift"] = True
                self.drift_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting data drift: {e}")
            return {"drift_detected": False, "error": str(e)}
    
    def detect_quality_drift(self, quality_score: float) -> Dict:
        """
        Detect degradation in quality metrics over time.
        
        Args:
            quality_score: The overall quality score from evaluation
            
        Returns:
            Dictionary with drift detection results
        """
        if quality_score is None:
            return {"drift_detected": False, "reason": "No quality score provided"}
        
        # Store in history
        self.quality_scores.append(quality_score)
        
        # Need at least 10 samples for meaningful comparison
        if len(self.quality_scores) < 10:
            return {
                "drift_detected": False,
                "reason": "Insufficient samples",
                "sample_count": len(self.quality_scores)
            }
        
        try:
            # Calculate recent average (last 10)
            recent_avg = np.mean(list(self.quality_scores)[-10:])
            
            # Calculate overall average
            overall_avg = np.mean(list(self.quality_scores))
            
            # Check threshold
            threshold = self.thresholds.get("quality_threshold", 0.6)
            
            # Drift if recent average drops significantly
            drift_detected = recent_avg < threshold or recent_avg < (overall_avg * 0.8)
            
            result = {
                "drift_detected": bool(drift_detected),
                "recent_average": float(recent_avg),
                "overall_average": float(overall_avg),
                "threshold": threshold,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "quality_drift"
            }
            
            if drift_detected:
                logger.warning(
                    f"Quality drift detected! Recent: {recent_avg:.3f}, "
                    f"Overall: {overall_avg:.3f}"
                )
                self.drift_detected["quality_drift"] = True
                self.drift_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting quality drift: {e}")
            return {"drift_detected": False, "error": str(e)}
    
    def detect_all_drifts(
        self,
        input_text: str,
        response_text: str,
        quality_score: Optional[float] = None
    ) -> Dict:
        """
        Run all drift detection checks.
        
        Args:
            input_text: User input
            response_text: LLM response
            quality_score: Optional quality score from evaluation
            
        Returns:
            Dictionary with all drift detection results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "response_drift": self.detect_response_drift(response_text),
            "data_drift": self.detect_data_drift(input_text),
            "any_drift_detected": False
        }
        
        if quality_score is not None:
            results["quality_drift"] = self.detect_quality_drift(quality_score)
        
        # Check if any drift was detected
        results["any_drift_detected"] = any([
            results["response_drift"].get("drift_detected", False),
            results["data_drift"].get("drift_detected", False),
            results.get("quality_drift", {}).get("drift_detected", False)
        ])
        
        return results
    
    def get_drift_status(self) -> Dict:
        """Get current drift status."""
        return {
            "drift_detected": self.drift_detected.copy(),
            "recent_drift_events": len([
                d for d in self.drift_history[-20:]
                if d.get("drift_detected", False)
            ]),
            "total_drift_events": len(self.drift_history),
            "sample_counts": {
                "responses": len(self.response_embeddings),
                "inputs": len(self.input_embeddings),
                "quality_scores": len(self.quality_scores)
            },
            "baseline_status": {
                "response_baseline_set": self.baseline.get("baseline_embedding") is not None,
                "input_baseline_set": self.baseline.get("input_baseline_embedding") is not None,
                "baseline_age": self.baseline.get("baseline_timestamp")
            }
        }
    
    def reset_drift_state(self):
        """Reset drift detection state."""
        self.drift_detected = {
            "response_drift": False,
            "data_drift": False,
            "quality_drift": False
        }
        logger.info("Drift state reset")
    
    def get_drift_history(self, limit: int = 20) -> List[Dict]:
        """Get recent drift events."""
        return self.drift_history[-limit:]


# Global drift detector instance
drift_detector = DriftDetector()


def get_drift_detector() -> DriftDetector:
    """Get the global drift detector instance."""
    return drift_detector
